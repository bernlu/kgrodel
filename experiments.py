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
parser.add_argument('--jlt_fast', action="store_true")
parser.add_argument('-p', '--problem')
parser.add_argument('--loglevel')
parser.add_argument('--sampling')
args = parser.parse_args()

if args.loglevel:
      nk.engineering.setLogLevel(args.loglevel)

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
print('jlt_fast: ', args.jlt_fast)
print('problem: ', args.problem)
print('sampling: ', args.sampling)

G = nk.readGraph(args.instance)
G = nk.components.ConnectedComponents(G).extractLargestConnectedComponent(G, True)
G.removeMultiEdges()
G.removeSelfLoops()

nk.overview(G)

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

if args.jlt_fast:
    jltLossCorrection = False
else:
    jltLossCorrection = True
    
if args.sampling:
    if args.sampling == 'MAX_DIAG':
        sampling = nk.robustness.SamplingVariant.MAX_DIAG
    if args.sampling == 'MIN_DIAG':
        sampling = nk.robustness.SamplingVariant.MIN_DIAG
    if args.sampling == 'UNIFORM':
        sampling = nk.robustness.SamplingVariant.UNIFORM

# --jlt            -> jlt=True, lossCorrection = True
# --jlt --jlt-fast -> jlt=True, lossCorrection = False

if args.algorithm == 'stGreedy':
    alg = nk.robustness.StGreedy(G, args.k, problem)
elif args.algorithm == 'simplStoch':
    alg = nk.robustness.SimplStoch(G, args.k, problem, args.eps, useJLT=jlt, jltLossCorrection=jltLossCorrection)
elif args.algorithm == 'colStoch':
    alg = nk.robustness.ColStoch(G, args.k, problem, args.eps, useJLT=jlt, jltLossCorrection=jltLossCorrection,  samplingVariant=sampling)
elif args.algorithm == 'specStoch':
	alg = nk.robustness.SpecStoch(G, args.k, problem, args.eps, args.ne)


before = datetime.now()
alg.run()
after = datetime.now()

elapsed = after - before
print('time: ', elapsed)
print('value: ', alg.getResultValue())
print('items: ', alg.getResultItems())


## compute exact value for analysis:bool_t
G = nk.readGraph(args.instance)
G = nk.components.ConnectedComponents(G).extractLargestConnectedComponent(G, True)
G.removeMultiEdges()
G.removeSelfLoops()

forestCenter = G.addNode()
for node in G.iterNodes():
    if node != forestCenter:
        G.addEdge(node, forestCenter)
lpsolv = nk.robustness.DynLazyLaplacianInverseSolver(G, 1e-6)
lpsolv.run()
totalValue = 0
for u,v in alg.getResultItems():
    ev = nk.dynamics.GraphEvent(nk.dynamics.GraphEventType.EDGE_REMOVAL, u, v, 1)
    totalValue = totalValue + lpsolv.totalResistanceDifference(ev)
    G.removeEdge(u,v)
    lpsolv.update(ev)

print('exact value: ', totalValue)