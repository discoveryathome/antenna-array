import copy,json,tempfile
from pathlib import Path
import pytest
from src.readiness import check_candidate,OUT

def test_candidate_task_binding_and_margin():
 p=json.loads((OUT/'portfolio.json').read_text());task=p['tasks'][1];c=task['incumbent']
 with tempfile.TemporaryDirectory() as tmp:
  file=Path(tmp)/'candidate.json';file.write_text(json.dumps(c));check_candidate(file,task['id'])
  for field,value in [('class','amplitude-reference'),('target','different-target')]:
   bad=copy.deepcopy(c);bad[field]=value;file.write_text(json.dumps(bad))
   with pytest.raises(ValueError):check_candidate(file,task['id'])
  bad=copy.deepcopy(c);bad['phases_rad'][0]+=.0001;file.write_text(json.dumps(bad))
  with pytest.raises(ValueError):check_candidate(file,task['id'])
