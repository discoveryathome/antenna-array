"""Local seeded task draw; does not claim work or enable donor intake."""
import argparse,json,secrets
from .run import ROOT

def main():
    p=argparse.ArgumentParser();p.add_argument('--seed');a=p.parse_args();seed=a.seed or secrets.token_hex(16)
    if len(seed)!=32:raise ValueError('seed must contain 32 hexadecimal digits')
    number=int(seed[:8],16);cardnumber=int(seed[8:16],16);int(seed,16)
    tracks=json.loads((ROOT/'discover/catalog.json').read_text())['tracks'];slot=number%sum(t['weight'] for t in tracks)
    for track in tracks:
        if slot<track['weight']:break
        slot-=track['weight']
    card=track['tasks'][cardnumber%len(track['tasks'])]
    print(json.dumps(dict(seed=seed,track=track['id'],task=card['id'],first_step=card['first_step'],intake='paused: local proposal; no consenting maintainer',coordination='discover/coordination.json'),indent=2))
if __name__=='__main__':main()
