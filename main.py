"""
excerpt from days of our lives:
Liz was married to Tony. Neither loved the other, and, indeed, Liz was in love
with Neil.  However, unknown to either Tony or Neil, Stephano, Tony’s father,
who wanted Liz to produce a grandson for him, threatened Liz that if she left
Tony, he would kill Neil. Liz told Neil that she did not love him, that she was
still in love with Tony, and that he should forget about her. Eventually, Neil
was convinced and he married Marie. Later, when Liz was finally free from Tony
(because Stephano had died), Neil was not free to marry her and their trouble
went on.
"""
from storymaker.human import Human
from pygoap.environment2d import Environment2D
from pygoap.goals import *
from pygoap.precepts import *
import asyncio

# logging.basicConfig(level=logging.DEBUG)


# attempt to model a complex relationship between actors.
# modeled after a soap opera, for ultimate drama
def build():
    env = Environment2D()

    liz = Human(name="liz", sex=1)
    liz.model()
    env.add(liz)
    env.set_position(liz, (0, 0))

    tony = Human(name="tony", sex=0)
    tony.model()
    env.add(tony)
    env.set_position(tony, (10, 10))

    neil = Human(name="neil", sex=0)
    neil.model()
    env.add(neil)
    env.set_position(neil, (10, 0))

    stephano = Human(name="stephano", sex=0)
    stephano.model()
    env.add(stephano)
    env.set_position(stephano, (0, 10))

    marie = Human(name="marie", sex=1)
    marie.model()
    env.add(marie)
    env.set_position(marie, (5, 5))

    def datum_goal(actor, key, value):
        return PreceptGoal(DatumPrecept(actor, key, value))

    # plant seeds of the simulation
    stephano.goals.add(datum_goal(liz, "has baby", True))
    liz.goals.add(datum_goal(liz, "married", neil))
    neil.goals.add(datum_goal(neil, "married", liz))
    marie.goals.add(datum_goal(marie, "married", neil))

    # inject environment state
    liz.process(DatumPrecept(liz, "married", tony))
    tony.process(DatumPrecept(tony, "married", liz))

    return env


if __name__ == '__main__':
    def tick():
        print(("== {:>8} {}".format(round(env.time, 2), "=" * 90)))
        env.update(1)
        loop.call_later(1, tick)

    env = build()
    env.start()
    loop = asyncio.get_event_loop()
    loop.call_soon(tick)
    loop.run_forever()
