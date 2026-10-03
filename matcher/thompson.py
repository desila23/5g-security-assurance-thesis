from matcher.ast import Atom, Sequence, Optional, PatternNode
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

        return self._compile_node(node)


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


    def _compile_node(self, node: PatternNode) -> NFA:
        if isinstance(node, Atom):
            return self._compile_atom(node)

        if isinstance(node, Sequence):
            return self._compile_sequence(node)

        if isinstance(node, Optional):
            return self._compile_optional(node)

        raise TypeError(
            f"Unsupported AST node: {type(node).__name__}"
        )


    def _compile_optional(self, optional: Optional) -> NFA:
        if not optional.items:
            raise ValueError(
                "Optional block cannot be empty"
            )

        start = self._new_state()
        end = self._new_state()

        inner = self._compile_sequence(Sequence(optional.items))

        transitions = []


        # PERCORSO 1: salto completamente il blocco opzionale.
        transitions.append(
            Transition(
                source=start,
                target=end,
                atom=None
            )
        )


        # PERCORSO 2: entro nel blocco opzionale.
        transitions.append(
            Transition(
                source=start,
                target=inner.start_state,
                atom=None
            )
        )
        transitions.extend(inner.transitions)    

        # Uscita dal blocco opzionale.
        transitions.append(
            Transition(
                source=inner.accept_state,
                target=end,
                atom=None
            )
        )


        return NFA(
            start_state=start,
            accept_state=end,
            transitions=transitions
        )


    
    def _compile_sequence(self, sequence: Sequence) -> NFA:
        if not sequence.items:
            raise ValueError("Sequence cannot be empty")

        fragments = [
            self._compile_node(item)
            for item in sequence.items
        ]

        transitions = []

        for fragment in fragments:
            transitions.extend(fragment.transitions)

        for current, following in zip(fragments, fragments[1:]):
            transitions.append(
                Transition(
                    source=current.accept_state,
                    target=following.start_state,
                    atom=None
                )
            )

        return NFA(
            start_state=fragments[0].start_state,
            accept_state=fragments[-1].accept_state,
            transitions=transitions
        )