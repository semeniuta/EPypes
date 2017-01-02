import random

def parse_transition_func(tf_dict):
    pe = dict()
    for se_pair, new_s in tf_dict.items():
        s, e = se_pair
        if s not in pe:
            pe[s] = [e]
        else:
            pe[s].append(e)

    return pe

def get_random_next_event(fsm):
    ce = fsm.current_events
    n = len(ce)
    if n == 1:
        return ce[0]
    else:
        i = random.randint(0, n-1)
        return ce[i]

class FSM:
    '''
    Finite-state machine

    Example of usage:

    simple_fsm = FSM('idle', {('idle', 'start'): 'running', ('running', 'stop'): 'idle'})
    '''

    def __init__(self, start, transition_func):
        self._start = start
        self._transition_func = transition_func
        self._possible_events = parse_transition_func(transition_func)

        self._current = start

    @property
    def current_events(self):
        return self._possible_events[self._current]

    def advance(self, event):
        if not event in self.current_events:
            raise Exception()

        self._current = self._transition_func[(self._current, event)]

    def advance_random(self):
        self.advance(get_random_next_event(self))
