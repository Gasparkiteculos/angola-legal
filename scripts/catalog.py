#!/usr/bin/env python3
"""Read-only search and version tools for Angola Legal metadata."""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; RECORDS=ROOT/"records"/"angola"
def rows(): return [(p,json.loads(p.read_text(encoding="utf-8"))) for p in sorted(RECORDS.glob("*.json"))]
def flat(x): return " ".join(flat(v) for v in x.values()) if isinstance(x,dict) else " ".join(flat(v) for v in x) if isinstance(x,list) else str(x)
def main():
 p=argparse.ArgumentParser(description=__doc__); s=p.add_subparsers(dest="cmd",required=True)
 a=s.add_parser("search"); a.add_argument("query")
 b=s.add_parser("versions"); b.add_argument("record_id",nargs="?")
 c=s.add_parser("diff"); c.add_argument("left"); c.add_argument("right")
 x=p.parse_args()
 if x.cmd=="search":
  terms=x.query.casefold().split(); out=[]
  for f,r in rows():
   if all(t in flat(r).casefold() for t in terms): out.append({k:r.get(k) for k in ("record_id","title","official_identifier","verification_status","temporal_status","source_url")} | {"file":f.relative_to(ROOT).as_posix()})
  print(json.dumps(out,ensure_ascii=False,indent=2)); return 0
 if x.cmd=="versions":
  allrows=rows(); ids={r["record_id"] for _,r in allrows}
  for f,r in allrows:
   if x.record_id and r["record_id"]!=x.record_id: continue
   v=r.get("versioning",{}); print(json.dumps({"record_id":r["record_id"],"version":v,"parent_present":v.get("version_of") in ids if v.get("version_of") else None,"related_identifiers":r.get("related_identifiers",[])},ensure_ascii=False))
  return 0
 a=json.loads(Path(x.left).read_text(encoding="utf-8")); b=json.loads(Path(x.right).read_text(encoding="utf-8")); changes=[]
 def walk(u,v,key=""):
  if isinstance(u,dict) and isinstance(v,dict):
   for k in sorted(set(u)|set(v)): walk(u.get(k),v.get(k),key+"."+k if key else k)
  elif u!=v: changes.append(key or "<root>")
 walk(a,b); print(json.dumps({"changed_fields":changes,"source_artifact_changed":a.get("versioning",{}).get("source_sha256")!=b.get("versioning",{}).get("source_sha256")},ensure_ascii=False,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
