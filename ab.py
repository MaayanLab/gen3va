
# Input
A = [['A',1], ['B',1], ['C',1], ['D',1]]
B = [['C',-1], ['D',-1], ['E',-1], ['F',-1]]

# Output
A  = [['A',1], ['B',1], ['C',1],  ['D',1],  ['E',0],  ['F',0]]
B  = [['A',0], ['B',0], ['C',-1], ['D',-1], ['E',-1], ['F',-1]]
AB = [['A',1], ['B',1], ['C',0],  ['D',0],  ['E',-1], ['F',-1]]