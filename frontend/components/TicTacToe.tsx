import React, { useState } from "react";

enum CellState {
    Empty = "-",
    X = "X",
    O = "O",
}
const STRING_TO_CELL_STATE: {[key: string]: CellState} = {
    "-": CellState.Empty,
    "X": CellState.X,
    "O": CellState.O,
};

interface SquareProps {
    state: CellState;
    callback: React.MouseEventHandler<HTMLButtonElement>;
}
const Square: React.FC<SquareProps> = ({state, callback}) => {
    return <button onClick={callback} disabled={state != CellState.Empty} style={{
        width: "50px",
        height: "50px",
        fontSize: "150%",
    }}>{state}</button>
}

async function getAgentAction(boardState: Array<CellState>) {
    const resp = await fetch(`${process.env.NEXT_PUBLIC_AGENT_API}/action`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            state: boardState,
            agent_is_x: false,
        }),
    });
    const rawAction = (await resp.json())["action"] as Array<string>;
    return rawAction.map((val) => STRING_TO_CELL_STATE[val]);
}

export default function TicTacToe() {
    const [boardState, update] = useState<Array<CellState>>(new Array(9).fill(CellState.Empty));
    const squareCallback = async (cellId: number) => {
        if (boardState[cellId] != CellState.Empty) {
            return;
        }

        const newBoardState = Array.from(boardState);
        newBoardState[cellId] = CellState.X;

        // TODO(richie): Improve this
        const agentAction = await getAgentAction(newBoardState);
        // Apply the agent's action
        const actionIndex = agentAction.findIndex(val => val != CellState.Empty);
        if (actionIndex == -1 || newBoardState[actionIndex] != CellState.Empty) {
            throw new Error("invalid action from agent")
        }
        newBoardState[actionIndex] = CellState.O;

        update(newBoardState);
    }

    const boardSquares = boardState.map((state, index) => <Square key={index} state={state} callback={(e) => squareCallback(index)} />)
    return (
        <table>
            <tbody>
                <tr>
                    <td>{boardSquares[0]}</td>
                    <td>{boardSquares[1]}</td>
                    <td>{boardSquares[2]}</td>
                </tr>
                <tr>
                    <td>{boardSquares[3]}</td>
                    <td>{boardSquares[4]}</td>
                    <td>{boardSquares[5]}</td>
                </tr>
                <tr>
                    <td>{boardSquares[6]}</td>
                    <td>{boardSquares[7]}</td>
                    <td>{boardSquares[8]}</td>
                </tr>
            </tbody>
        </table>
  );
};
