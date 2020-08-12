
import gc

def print_free_memory(full=False):
  F = gc.mem_free()
  A = gc.mem_alloc()
  T = F+A
  P = '{0:.2f}%'.format(F/T*100)
  if not full:
    print(P)
  else :
    print('Total:{0} Free:{1} ({2})'.format(T,F,P))

