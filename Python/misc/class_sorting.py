#===============================================================================
# Sort list of class instances
#===============================================================================
# How do I sort a list of class instances by an attribute?
# 
#===============================================================================
# Written for Python 3.7
# By Dan Fourquet
#===============================================================================

class Color:
    def __init__(self, id, color, rank):
        self.id = id
        self.color = color
        self.rank = rank

    def __repr__(self):
        return f'{self.color}: {self.rank}'

# Create a list containing color instances
colors = []

colors.append(Color(id=1, color='Blue', rank=1))
colors.append(Color(2, 'Green', 3))
colors.append(Color(3, 'Orange', 2))

# Create a list sorted by color rank
colorsSorted = sorted(colors, key=lambda x: x.rank)

print('unsorted:')
print(colors)
print('\nsorted:')
print(colorsSorted)