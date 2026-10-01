from matcher.ast import Atom, Sequence, PatternNode
from matcher.automaton import NFA, Transition

class ThompsonCompiler:
    """
    Compila un pattern AST in un NFA

    Per il momento supporta:
        - Atom
        - Sequence lineare

    Verrà esteso con:
        - Alternative
        - Optional
        - Repeat   
    """

    def __init__(self):
        self._next_state = 0


    def _new_state(self) -> int:
        state = self._next_state
        self._next_state += 1
        return state


    def compile(self, node: PatternNode) -> NFA:
        """
        Entry point del compilatore
        """

        self._next_state = 0

        if isinstance(node, Atom):
            return self._compile_atom(node)

        if isinstance(node, Sequence):
            return self._compile_sequence(node)

        raise TypeError(
            f"Unsupported AST node: {type(node).__name__}"
        )


    def _compile_atom(self, atom: Atom) -> NFA:
        start = self._new_state()
        end = self._new_state()

        transition = Transition(
            source=start,
            target=end,
            atom=atom
        )

        return NFA(
            start_state=start,
            accept_state=end,
            transitions=[transition]
        )


    def _compile_sequence(self, sequence: Sequence) -> NFA:
        if not sequence.items:
            raise ValueError("Sequence cannot be empty")

        start = self._new_state()
        current = start

        transitions = []

        for item in sequence.items:
            if not isinstance(item, Atom):
                raise TypeError(
                    "Only Atom nodes are currently supporter inside Sequence"
                )

            next_state = self._new_state()

            transitions.append(
                Transition(
                    source=current,
                    target=next_state,
                    atom=item
                )
            )

            current = next_state

        return NFA(
            start_state=start,
            accept_state=current,
            transitions=transitions
        )