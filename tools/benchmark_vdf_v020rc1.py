#!/usr/bin/env python3
import argparse,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from hashburst_tep.vdf.cg_weso import CGWesoV1

def main():
 p=argparse.ArgumentParser();p.add_argument("--iterations",type=int,default=4096);a=p.parse_args()
 v=CGWesoV1();challenge=bytes.fromhex("a5"*32)
 t=time.perf_counter();r=v.evaluate(challenge,a.iterations);te=time.perf_counter()-t
 t=time.perf_counter();ok=v.verify(challenge,r);tv=time.perf_counter()-t
 print(json.dumps({"schema":"hashburst-tep-vdf-benchmark-v1","suite":v.suite_id,"iterations":a.iterations,"evaluation_seconds":te,"verification_seconds":tv,"verification_ok":ok,"verification_faster":tv<te},sort_keys=True))
 return 0 if ok and tv<te else 1
if __name__=="__main__":raise SystemExit(main())
