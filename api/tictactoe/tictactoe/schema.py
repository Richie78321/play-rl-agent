state_schema = {
    "type": "array",
    "items": {
        "enum": ["-", "X", "O"],
    },
    # Exactly 9 elements required: one for each cell in a Tic-Tac-Toe board.
    "minItems": 9,
    "maxItems": 9,
}
