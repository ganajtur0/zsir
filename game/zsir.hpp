#ifndef ZSIR_H
#define ZSIR_H

#include "card.h"
#include "ismcts/game.h"
#include "ismcts/sosolver.h"
#include <vector>

class Zsir : public ISMCTS::POMGame<Card>
{	
public:
	explicit Zsir(unsigned int players = 2);
	virtual Clone cloneAndRandomise(Player observer) const override;
	virtual Player currentPlayer() const override;
	virtual std::vector<Player> players() const override;
	virtual std::vector<Card> validMoves() const override;
	virtual double getResult(Player player) const override;
	virtual void doMove(Card const move) override;
	friend std::ostream &operator<<(std::ostream &out, Zsir const &g);
    void AIMove(void);
#ifdef DEBUG
	void scoreTest(void);
	void playTest(void);
    void AITest(void);
#endif // DEBUG

protected:
	using Hand = std::vector<Card>;
	using Play = std::pair<Player, Card>;

	unsigned int static constexpr s_deckSize {32};
	std::vector<Card> m_deck { s_deckSize };
    std::vector<Card> m_deckUsed { s_deckSize };
	std::vector<Card> m_unknownCards;
	std::vector<Hand> m_playerCards;
	std::vector<Play> m_currentTrick;
	std::vector<unsigned int> m_scores;
	Player m_numPlayers;
	Player m_player {0};
	Player m_startingPlayer {0};
	std::vector<Player> m_players;
	Card::Szin m_requestSzin;
	bool m_gameOver = false;

	Player nextPlayer(Player p) const;
	void deal();
	void finishRound();
	Player roundWinner();
	void endGame(void);
	int trickValue(void) const;
};

#endif //ZSIR_H
