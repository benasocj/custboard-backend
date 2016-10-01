from datetime import datetime, timedelta
import math
from random import uniform

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

points = [math.sin(math.pi / (8 * 4) * i) * 7 + uniform(-.5, .5)
          for i in range(8 * 4)]
plt.figure(figsize=(10, 5))
plt.grid()
#plt.title('interval of {} minutes'.format(interval))
plt.plot(points)

plt.xlabel('time')
plt.ylabel('conversion [picks/h]')
plt.xticks(
    range(0, len(points) + 1, 4),
    [(datetime.min.replace(hour=7) + timedelta(minutes=15) * i)
        .strftime('%H:%M') for i in range(0, len(points) + 1, 4)],
    rotation=90)

plt.savefig('/tmp/graph.png', bbox_inches='tight')
plt.close()
