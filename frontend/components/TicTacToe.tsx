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
const WINNER_AGENT_REWARD: {[key: string]: number} = {
    // Human is X, so this is a loss.
    "X": -1,
    // Agent is O, so this is a win.
    "O": 1,
    // Otherwise it is either a tie or not the end of the game, so 0.
    "-": 0,
};
const GAME_RESTART_TIMEOUT_MS = 1000;

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

function isTie(board: GameState): boolean {
    return board.every((value) => value != CellState.Empty)
}

function isWinner(board: GameState): CellState {
    for (const player of [CellState.X, CellState.O]) {
        const winConditions = [
            // Horizontal win conditions
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],

            // Vertical win conditions
            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],

            // Diagonal win condition
            [0, 4, 8],

            // Anti-diagonal win condition
            [2, 4, 6],
        ];

        for (const winCondition of winConditions) {
            if (winCondition.every((index) => board[index] == player)) {
                return player;
            }
        }
    }

    return CellState.Empty
}

interface TicTacToeProps {}
interface TicTacToeState {
    boardState: GameState;
    loading: boolean;
}
interface AgentStep {
    initialState: GameState;
    action: GameState | null;
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

    async sendAgentStep(humanBoardState: GameState, action: GameState | null, winner: CellState) {
        if (this.lastAgentStep != null) {
            const playdata = {
                "initial_state": this.lastAgentStep.initialState,
                "action": this.lastAgentStep.action,
                "resultant_state": humanBoardState,
                "reward": WINNER_AGENT_REWARD[winner],
                "agent_is_x": false,
            };
            console.log("Sending playdata:")
            console.log(playdata)

            if (!process.env.NEXT_PUBLIC_DISABLE_PLAYDATA_PUSH) {
                await fetch(`${process.env.NEXT_PUBLIC_PLAYDATA_API}/submit`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(playdata),
                });
            }
        }

        // It is important that the GameState arrays are cloned -- otherwise downstream edits
        // can affect these values.
        this.lastAgentStep = {
            initialState: Array.from(humanBoardState),
            action: action == null ? null : Array.from(action),
        };
    }

    restartGame() {
        this.lastAgentStep = null;
        this.setState({
            ...this.state,
            boardState: new Array(9).fill(CellState.Empty),
            loading: false,
        })
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

            // Apply the human's turn.
            const humanBoardState = Array.from(this.state.boardState);
            humanBoardState[cellId] = CellState.X;
            // Determine if the human won or tied the game.
            let winner = isWinner(humanBoardState);
            let tie = isTie(humanBoardState);

            // Only conduct the agent's turn if there is no winner and no tie
            // after the human's turn.
            let agentAction: GameState | null = null;
            const agentBoardState = Array.from(humanBoardState);
            if (winner == CellState.Empty && !tie) {
                agentAction = await getAgentAction(humanBoardState);

                // Apply the agent's turn.
                const actionIndex = agentAction.findIndex(val => val != CellState.Empty);
                if (actionIndex == -1 || humanBoardState[actionIndex] != CellState.Empty) {
                    throw new Error("invalid action from agent")
                }
                agentBoardState[actionIndex] = CellState.O;

                // Determine if the agent won or tied the game.
                winner = isWinner(agentBoardState);
                tie = isTie(agentBoardState);
            }

            // We update with the humanBoardState and not the agentBoardState.
            // Otherwise we are double-counting the agentAction in the state and the action.
            await this.sendAgentStep(humanBoardState, agentAction, winner);

            // Update the game state.
            if (winner != CellState.Empty || tie) {
                // The game is over.
                this.setState({
                    ...this.state,
                    boardState: agentBoardState,
                    loading: true,
                })

                // Wait for some time and then restart the game
                await new Promise((resolve) => setTimeout(resolve, GAME_RESTART_TIMEOUT_MS))
                
                this.restartGame();
            } else {
                // The game is ongoing.
                this.setState({
                    ...this.state,
                    boardState: agentBoardState,
                    loading: false,
                });
            }
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
