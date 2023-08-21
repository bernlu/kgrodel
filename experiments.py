import networkit as nk

import argparse
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('algorithm')
parser.add_argument('-i', '--instance')
parser.add_argument('-k', type=int)
parser.add_argument('-eps', type=float)
parser.add_argument('-ne', type=int)
parser.add_argument('--jlt', action="store_true")
parser.add_argument('-p', '--problem')
args = parser.parse_args()


if not args.instance:
    print('error: instance required')
    raise RuntimeError('no instance provided!')

print('called with:')
print('algorithm: ', args.algorithm)
print('instance: ', args.instance)
print('k: ', args.k)
print('eps: ', args.eps)
print('ne: ', args.ne)
print('jlt: ', args.jlt)
print('problem: ', args.problem)

G = nk.readGraph(args.instance)
G = nk.components.ConnectedComponents(G).extractLargestConnectedComponent(G, True)

if args.problem == 'global_improvement':
    problem = nk.robustness.RobustnessProblem.GLOBAL_IMPROVEMENT
elif args.problem == 'global_reduction':
	problem = nk.robustness.RobustnessProblem.GLOBAL_REDUCTION
else:
     raise RuntimeError('error: no valid problem provided')

if args.jlt:
	jlt = True
else:
	jlt = False

if args.algorithm == 'stGreedy':
    alg = nk.robustness.StGreedy(G, args.k, problem)
elif args.algorithm == 'simplStoch':
    alg = nk.robustness.SimplStoch(G, args.k, problem, args.eps, useJLT=jlt)
elif args.algorithm == 'colStoch':
    alg = nk.robustness.ColStoch(G, args.k, problem, args.eps, useJLT=jlt)
elif args.algorithm == 'specStoch':
	alg = nk.robustness.SpecStoch(G, args.k, problem, args.eps, args.ne)


before = datetime.now()
alg.run()
after = datetime.now()

elapsed = after - before
print('time: ', elapsed)
print('value: ', alg.getResultValue())
print('items: ', alg.getResultItems())

