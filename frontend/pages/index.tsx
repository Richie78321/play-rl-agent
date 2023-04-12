import Head from 'next/head'
import TicTacToe from '@/components/TicTacToe'

const mainStyle = {
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  margin: "auto",
  height: "100%",
}

export default function Home() {
  return (
    <>
      <Head>
        <title>Play RL Agent</title>
        <meta name="description" content="Play an RL agent in Tic-Tac-Toe" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
        <link rel="manifest" href="/site.webmanifest" />
      </Head>
      <main style={mainStyle}>
        <TicTacToe />
      </main>
    </>
  )
}
