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
const Sqaure: React.FC<SquareProps> = ({state, callback}) => {
    return <button onClick={callback} disabled={state != CellState.Empty}>{state}</button>
}

export default function TicTacToe() {
    return (
        <>
            <Sqaure state={CellState.X} callback={(e) => {}} />
            <Sqaure state={CellState.O} callback={(e) => {}} />
            <Sqaure state={CellState.Empty} callback={(e) => {}} />
        </>
  );
};
