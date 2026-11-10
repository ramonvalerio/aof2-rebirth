"""SPEC-079: execute impact and delayed-launch branches with Unicorn M68000.
The native reaction initializer is stubbed; this does not test gameplay.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_rom import load_patch
from asm68k import assemble,JmpNext,JmpAbs
from unicorn import *
from unicorn.m68k_const import *
patch=load_patch('characters/ryo/zanretsuken-three-buttons')
reaction=load_patch('global/uppercut-juggle').blocks[0].program
programs={b.name:b.program for b in patch.blocks if hasattr(b,'program')}
def put(u,a,v,n=1):u.mem_write(a,v.to_bytes(n,'big'))
def setup(program):
 u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000)
 u.mem_write(0x60000,assemble([JmpAbs(0x70000) if isinstance(i,JmpNext) else i for i in program],0x60000))
 u.reg_write(UC_M68K_REG_SR,0x2000);u.reg_write(UC_M68K_REG_A7,0x10f000)
 for reg,v in [(UC_M68K_REG_A0,0x109280),(UC_M68K_REG_A6,0x109380),(UC_M68K_REG_A4,0x10a000),(UC_M68K_REG_A5,0x108000)]:u.reg_write(reg,v)
 return u
def run(u,stops):
 seen=[]
 def hook(u,a,size,data):
  if a in stops:seen.append(a);u.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x60000,0,count=500)
 assert seen
 return seen[0]
count=0
for variant in (1,2,3):
 for anim in (0x23a,0x23b,0x14d):
  for guard in (0,3):
   u=setup(programs['zan_ex_impact']);a=0x109280;b=0x109380
   for off,v,n in [(0x62,1,2),(0x230,0x44,2),(0x3c2,variant,1),(0x6e,0x414e,2),(3,0x10,1)]:put(u,a+off,v,n)
   put(u,0x109000+0x54,anim,2)
   put(u,b+0x7c,guard);run(u,[0x70000])
   expected=variant==3 and anim==0x23b and guard!=3
   assert bool(u.mem_read(b+0x24b,1)[0]&128)==expected
   assert int.from_bytes(u.mem_read(b+0xa5e,2),'big')==(0x140 if expected else 0)
   assert u.reg_read(UC_M68K_REG_A7)==0x10f000
   count+=1
# Delayed reaction must launch even after attacker changes animation/command.
for char in range(1,13):
 for guard in (0,3):
  for life in (0,100):
   u=setup(reaction);a=0x109280;b=0x109380
   put(u,a+0x62,1,2);put(u,a+0x230,1,2);put(u,a+0x6e,1,2)
   put(u,b+0x62,char,2);put(u,b+0x6c,life,2);put(u,b+0xa6a,0x44,2);put(u,b+0x24b,0x80);put(u,b+0x7c,guard)
   u.mem_write(0x20604,bytes.fromhex('4e75'))
   put(u,0x10effc,0x70000,4);u.reg_write(UC_M68K_REG_A7,0x10eff4)
   expected=life>0 and guard!=3
   assert run(u,[0x70000,0x2134c])==(0x70000 if expected else 0x2134c)
   if expected:
    assert int.from_bytes(u.mem_read(b+0x6e,2),'big')==0x790+char
    assert int.from_bytes(u.mem_read(b+0x28,4),'big')==0x80000
    assert int.from_bytes(u.mem_read(b+0x38,2),'big')==0xffc0
    assert u.reg_read(UC_M68K_REG_A7)==0x10f000
   count+=1
print('PASS',count,'impact and delayed launch cases; native reaction initializer stubbed')

# Hien impact is scoped to the final contact, not played as a swing sound.
import importlib.util
spec=importlib.util.spec_from_file_location('zan',Path(__file__).resolve().parent.parent/'patches/characters/ryo/zanretsuken-three-buttons/patch.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
assert bytes.fromhex('c70140') not in mod.EX_CMD
assert bytes.fromhex('c70172') in mod.EX_CMD
print('PASS EX uses Hien impact $0140 on hit, without playing it on whiff')

# Integration: execute the built ROM's sequence transition, complete contact
# chain and sound selector. Only the hardware sound send is intercepted.
import zipfile
from build_rom import swap16
root=Path(__file__).resolve().parent.parent
rom=bytes(swap16(zipfile.ZipFile(root/'rom/aof2r.zip').read('056-p1.p1')))
def rom_cpu():
 u=setup([]);u.mem_write(0,rom);return u
def call_rom(u,start,sounds=None):
 end=0x70000
 put(u,0x10effc,end,4);u.reg_write(UC_M68K_REG_A7,0x10effc)
 reached=[]
 def trace(u,pc,size,data):
  if pc==end:reached.append(pc);u.emu_stop()
  elif pc==0x9ba and sounds is not None:
   sounds.append(u.reg_read(UC_M68K_REG_D0)&0xffff)
   sp=u.reg_read(UC_M68K_REG_A7)
   ret=int.from_bytes(u.mem_read(sp,4),'big')
   u.reg_write(UC_M68K_REG_A7,sp+4);u.reg_write(UC_M68K_REG_PC,ret)
 h=u.hook_add(UC_HOOK_CODE,trace)
 try:u.emu_start(start,0,count=3000)
 finally:u.hook_del(h)
 assert reached,hex(u.reg_read(UC_M68K_REG_PC))
 assert u.reg_read(UC_M68K_REG_A7)==0x10f000

a,b,sprite=0x109280,0x109380,0x109000
u=rom_cpu();u.reg_write(UC_M68K_REG_A6,sprite)
put(u,a+0x6e,0x414e,2);put(u,sprite+0x54,0x814c,2)
put(u,sprite+0x5f,0x80);put(u,sprite+0x4c,0x10e000,4);put(u,0x10e000,0x23b,2)
call_rom(u,0x4a8e)
assert int.from_bytes(u.mem_read(sprite+0x54,2),'big')==0x23b
assert int.from_bytes(u.mem_read(a+0x6e,2),'big')==0x414e
print('PASS native sequence changes sprite $54, while actor $6E stays $414E')

for q in (0,1,2):
 u=setup(programs['zan_ex_frame']);u.reg_write(UC_M68K_REG_A6,sprite)
 for off,v,n in [(0x62,1,2),(0x230,0x44,2),(0x3c2,3,1),(0x6e,0x414e,2),(0x3aa,0,1)]:put(u,a+off,v,n)
 put(u,sprite+0xb,0x13);put(u,sprite+0x54,0x23b,2);put(u,sprite+0x5a,q)
 put(u,sprite+7,0x11);put(u,sprite+8,0x12)
 put(u,0x109170,0x81);put(u,0x109270,0x81)
 run(u,[0x70000])
 assert u.mem_read(a+0x3aa,1)[0]==int(q==0)
 assert u.mem_read(0x109170,1)[0]==(1 if q==0 else 0x81)
 assert u.mem_read(0x109270,1)[0]==(1 if q==0 else 0x81)

observed={}
for move in ('hien','zan_ex'):
 u=rom_cpu()
 put(u,a+0x62,1,2);put(u,a+3,0x10);put(u,b+0x64,a,4)
 put(u,b+0x6c,100,2);put(u,sprite+0xb,0x13)
 if move=='hien':
  # Native E7 handler consumes the actual Hien sound operand from its stream.
  off=rom.index(bytes.fromhex('e70140'),0x533bc,0x533e0)+1
  u.reg_write(UC_M68K_REG_A0,off);u.reg_write(UC_M68K_REG_A6,sprite)
  call_rom(u,0x2299e)
  put(u,a+0x230,0x46,2);put(u,a+0x6e,0x13e,2)
 else:
  put(u,a+0x230,0x44,2);put(u,a+0x6e,0x414e,2)
  put(u,a+0x3c2,3);put(u,a+0x3aa,1);put(u,sprite+0x54,0x23b,2)
 u.reg_write(UC_M68K_REG_A6,b)
 call_rom(u,0x2248e)
 assert int.from_bytes(u.mem_read(b+0xa5e,2),'big')==0x140,move
 sounds=[];call_rom(u,0x21e34,sounds)
 assert sounds==[0x140],(move,sounds)
 assert int.from_bytes(u.mem_read(b+0xa5e,2),'big')==0
 observed[move]=sounds
assert observed['hien']==observed['zan_ex']
print('PASS built ROM: Hien and Zan EX each send the same single sound $0140 through the native contact/sound pipeline')
