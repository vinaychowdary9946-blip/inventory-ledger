import unittest,tempfile,os
from concurrent.futures import ThreadPoolExecutor
from ledger import Ledger
class LedgerTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.path=os.path.join(self.tmp.name,'l.db'); self.l=Ledger(self.path)
 def tearDown(self): self.l.close(); self.tmp.cleanup()
 def test_replay_and_compensation(self):
  self.l.adjust('a','S',10,0,'receipt'); self.l.adjust('b','S',-3,1,'shipment'); self.l.adjust('c','S',3,2,'return')
  self.assertEqual(self.l.state('S'),{'sku':'S','quantity':10,'version':3}); self.assertEqual(sum(e['delta'] for e in self.l.events('S')),10)
 def test_oversell_rolls_back(self):
  self.l.adjust('a','S',2,0,'receipt')
  with self.assertRaises(ValueError): self.l.adjust('b','S',-3,1,'shipment')
  self.assertEqual(len(self.l.events()),1)
 def test_idempotency(self):
  a=self.l.adjust('a','S',10,0,'receipt'); self.assertEqual(a,self.l.adjust('a','S',10,0,'receipt'))
  with self.assertRaises(ValueError): self.l.adjust('a','S',20,0,'receipt')
 def test_version_conflict(self):
  self.l.adjust('a','S',10,0,'receipt')
  with self.assertRaises(ValueError): self.l.adjust('b','S',-1,0,'shipment')
 def test_concurrent_oversell(self):
  self.l.adjust('a','S',1,0,'receipt')
  def run(i):
   l=Ledger(self.path)
   try:
    l.adjust(str(i),'S',-1,1,'shipment'); return True
   except ValueError: return False
   finally: l.close()
  with ThreadPoolExecutor(max_workers=2) as p: results=list(p.map(run,[1,2]))
  self.assertEqual(sum(results),1); self.assertEqual(self.l.state('S')['quantity'],0)
 def test_restart(self):
  self.l.adjust('a','S',5,0,'receipt'); self.l.close(); self.l=Ledger(self.path); self.assertEqual(self.l.state('S')['quantity'],5)
 def test_validation(self):
  for delta in [0,True,1.5]:
   with self.assertRaises(ValueError): self.l.adjust('a','S',delta,0,'receipt')
if __name__=='__main__': unittest.main()
