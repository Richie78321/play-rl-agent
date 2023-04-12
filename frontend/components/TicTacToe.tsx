import React from "react";

enum CellState {
    Empty = "-",
    X = "X",
    O = "O",
}
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

export default function TicTacToe() {
    // Test board
    // X O -
    // X - -
    // - - -
    const boardState: Array<CellState> = [CellState.X, CellState.O, CellState.Empty, CellState.X, CellState.Empty, CellState.Empty, CellState.Empty, CellState.Empty, CellState.Empty]
    const boardSquares = boardState.map((state, index) => <Square state={state} callback={(e) => {}} />)
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
