import React, { Component } from "react";
import { Mutex } from "async-mutex";

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

type GameState = Array<CellState>;

interface SquareProps {
    state: CellState;
    callback: React.MouseEventHandler<HTMLButtonElement>;
    disabled: boolean;
}
const Square: React.FC<SquareProps> = ({state, callback, disabled}) => {
    return <button onClick={callback} disabled={disabled || state != CellState.Empty} style={{
        width: "50px",
        height: "50px",
        fontSize: "150%",
    }}>{state}</button>
}

async function getAgentAction(boardState: GameState): Promise<GameState> {
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


interface TicTacToeProps {}
interface TicTacToeState {
    boardState: GameState;
    loading: boolean;
}
interface AgentStep {
    initialState: GameState;
    action: GameState;
}
export default class TicTacToe extends Component<TicTacToeProps, TicTacToeState> {
    lastAgentStep: AgentStep | null;
    gameMutex: Mutex;
    
    constructor(props: TicTacToeProps) {
        super(props);

        this.state = {
            boardState: new Array(9).fill(CellState.Empty),
            loading: false,
        };
        this.gameMutex = new Mutex();
        this.lastAgentStep = null;
    }

    async sendAgentStep(state: GameState, action: GameState) {
        // It is important that the GameState arrays are cloned -- otherwise downstream edits
        // can affect these values.
        
        if (this.lastAgentStep != null) {
            // TODO(richie): Send this to playdata API
            console.log({
                "initial_state": this.lastAgentStep.initialState,
                "action": this.lastAgentStep.action,
                "resultant_state": Array.from(state),
            });
        }

        this.lastAgentStep = {
            initialState: Array.from(state),
            action: Array.from(action),
        };
    }

    render() {
        const squareCallback = async (cellId: number) => {
            // Even though JavaScript is single-threaded, we use a mutex to ensure
            // that only one callback runs this section at a time.
            await this.gameMutex.acquire()
            this.setState({
                ...this.state,
                loading: true,
            });

            if (this.state.boardState[cellId] != CellState.Empty) {
                return;
            }
    
            const newBoardState = Array.from(this.state.boardState);
            newBoardState[cellId] = CellState.X;
    
            const agentAction = await getAgentAction(newBoardState);
            // Apply the agent's action
            const actionIndex = agentAction.findIndex(val => val != CellState.Empty);
            if (actionIndex == -1 || newBoardState[actionIndex] != CellState.Empty) {
                throw new Error("invalid action from agent")
            }
            await this.sendAgentStep(newBoardState, agentAction);
            newBoardState[actionIndex] = CellState.O;

            this.setState({
                ...this.state,
                boardState: newBoardState,
                loading: false,
            });
            await this.gameMutex.release()
        }
    
        const boardSquares = this.state.boardState.map((state, index) => <Square key={index} state={state} disabled={this.state.loading} callback={(e) => squareCallback(index)} />)
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
    }
}
