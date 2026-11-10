"""Regression checks for SPEC-080; requires Unicorn (M68000) and a built ROM.
Run: python tools/check_desperation_priority.py
Executes the patch code, without running a match or the emulator frontend.
"""
from pathlib import Path
import sys,zipfile,re
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))
from build_rom import swap16
from unicorn import *
from unicorn.m68k_const import *
r=bytes(swap16(zipfile.ZipFile(ROOT/'rom/aof2r.zip').read('056-p1.p1')))
HOOKS={'desp_filter':0xF6B98,'desp_clash':0x22DA2,'desp_throw':0x1DC14}
def addr(name):
 h=HOOKS[name];assert r[h:h+2]==bytes.fromhex('4ef9')
 return int.from_bytes(r[h+2:h+6],'big')
def setup():
 u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,r)
 u.reg_write(UC_M68K_REG_SR,0x2000);u.reg_write(UC_M68K_REG_A7,0x10f000)
 u.reg_write(UC_M68K_REG_A5,0x108000)
 return u
def put(u,a,v,n=1):u.mem_write(a,v.to_bytes(n,'big'))
def run(u,start,stops):
 found=[]
 def stop(u,a,size,data):
  if a in stops:found.append(a);u.emu_stop()
 u.hook_add(UC_HOOK_CODE,stop)
 try:u.emu_start(start,0,count=500)
 except UcError:
  print('CPU unsupported at',hex(u.reg_read(UC_M68K_REG_PC)),bytes(u.mem_read(u.reg_read(UC_M68K_REG_PC),10)).hex());raise
 assert found,hex(u.reg_read(UC_M68K_REG_PC))
 assert u.reg_read(UC_M68K_REG_A7)==0x10f000
 return found[0]
def actor(u,a,enabled,state=3,match=True):
 put(u,a+0x3c3,enabled);put(u,a+0x40,state);put(u,a+0x230,0x44,2);put(u,a+0x3c4,0x44 if match else 0x45,2)
count=0
for reverse in (False,True):
 for enabled in (0,1):
  for kind in ('normal','desp_body','projectile','desp_projectile'):
   for state in (1,3,6):
    for match in (False,True):
     u=setup();source=0x109000;body=0x10a000;sprite=0x10a500;defender=0x109380
     put(u,body+2,0x20);put(u,body+0xb,0x25);put(u,sprite+3,0x20);put(u,sprite+0xb,0x14)
     actor(u,defender,enabled,state,match)
     if 'projectile' in kind:put(u,source+0x6f,0x80);put(u,source+0x80,int(kind=='desp_projectile'))
     u.reg_write(UC_M68K_REG_A6,body if reverse else source);u.reg_write(UC_M68K_REG_A4,source if reverse else body)
     protected=enabled and state==3 and match
     expected=0xf6bd6 if protected and kind!='desp_projectile' else 0xf6b9e
     assert run(u,addr('desp_filter'),[0xf6bd6,0xf6b9e])==expected,(reverse,enabled,kind,state,match)
     assert u.reg_read(UC_M68K_REG_A6)==(body if reverse else source)
     assert u.reg_read(UC_M68K_REG_A4)==(source if reverse else body)
     count+=1
for own in (0,1):
 for other in (0,1):
  u=setup();u.reg_write(UC_M68K_REG_A6,0x109000);u.reg_write(UC_M68K_REG_D1,0x2000)
  put(u,0x109080,own);put(u,0x10a080,other)
  expected=0x22da8 if not own and not other else (0x22dc4 if own and not other else 0x22dce)
  assert run(u,addr('desp_clash'),[0x22da8,0x22dc4,0x22dce])==expected
  count+=1
print('PASS',count,'collision/priority cases, both player directions and inactive markers')


from build_rom import load_patch
from asm68k import assemble,JmpNext,JmpAbs
patch=load_patch('global/desperation-priority')
programs={b.name:b.program for b in patch.blocks}
def standalone(u,name):
 code=assemble([JmpAbs(0x70000) if isinstance(x,JmpNext) else x for x in programs[name]],0x60000)
 u.mem_write(0x60000,code);return 0x60000
moves=(0x22,0x47,0x6a,0x8d,0xb5,0xd8,0x100,0x117,0x142,0x162,0x185,0x1a0)
for char in range(1,14):
 for correct in (False,True):
  u=setup();a=0x109280;u.reg_write(UC_M68K_REG_A6,a);put(u,a+0x62,char,2)
  put(u,a+0x3c3,1);put(u,0x108010,moves[char-1] if char<=12 and correct else 0x555,2);put(u,0x108020,0x48,2)
  run(u,standalone(u,'desp_start'),[0x70000])
  assert u.mem_read(a+0x3c3,1)[0]==int(char<=12 and correct)
  count+=1
for enabled in (0,1):
 for state in (1,3,6):
  for match in (False,True):
   u=setup();a=0x109280;proj=0x10a000;actor(u,a,enabled,state,match)
   u.reg_write(UC_M68K_REG_A6,a);u.reg_write(UC_M68K_REG_A0,proj);put(u,proj+0x80,1)
   run(u,standalone(u,'desp_spawn'),[0x70000])
   assert u.mem_read(proj+0x80,1)[0]==int(enabled and state==3 and match)
   assert u.reg_read(UC_M68K_REG_A0)==proj
   count+=1
for enabled in (0,1):
 for state in (1,3,6):
  for match in (False,True):
   for native in (0,2):
    u=setup();a=0x109280;b=0x109380;actor(u,b,enabled,state,match)
    put(u,a+0x64,b,4);put(u,a+0xa68,native);u.reg_write(UC_M68K_REG_A6,a)
    put(u,0x10effc,0x70000,4);u.reg_write(UC_M68K_REG_A7,0x10effc)
    run(u,addr('desp_throw'),[0x70000])
    expected_z=bool(enabled and state==3 and match) or not native
    assert bool(u.reg_read(UC_M68K_REG_SR)&4)==expected_z
    count+=1
print('PASS',count,'total cases, including selection, projectile lifecycle and throw immunity')

# Attack children must stay active even while their owner is invincible.
for reverse in (False,True):
 u=setup();source=0x109000;attack=0x10a000;sprite=0x10a500
 put(u,attack+2,0x20);put(u,attack+0xb,0x25);put(u,sprite+7,0x20);put(u,sprite+0xb,0x14)
 actor(u,0x109380,1)
 u.reg_write(UC_M68K_REG_A6,attack if reverse else source);u.reg_write(UC_M68K_REG_A4,source if reverse else attack)
 assert run(u,addr('desp_filter'),[0xf6bd6,0xf6b9e])==0xf6b9e
print('PASS attack boxes remain active for both players (164 cases total)')
