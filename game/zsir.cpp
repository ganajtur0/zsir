#include "zsir.hpp"

#include <algorithm>
#include <memory>
#include <numeric>
#include <iterator>
#include <vector>
#include <random>
#include <iostream>

namespace{

	inline std::mt19937 &prng() {
		std::mt19937 static thread_local prng;
		return prng;
	}

}

void Zsir::deal(){

	std::shuffle(m_deckUsed.begin(), m_deckUsed.end(), prng());

	for (auto p : m_players) {
		auto &hand = m_playerCards[p];
		
		for (char to = 4 - hand.size(); to > 0 && m_deckUsed.size() > 0; --to){
			hand.push_back(m_deckUsed.back());
            m_deckUsed.pop_back();
        }

	}
    m_unknownCards.clear();
    std::copy(m_deckUsed.begin(), m_deckUsed.end(), std::back_inserter(m_unknownCards));
}

Zsir::Clone Zsir::cloneAndRandomise(Player observer) const
{
	auto clone = std::make_unique<Zsir>(*this);
    Hand unseenCards = m_unknownCards;
    for (auto p : m_players) {
        if (p == observer)
            continue;
        auto const &hand = m_playerCards[p];
        unseenCards.insert(unseenCards.end(), hand.begin(), hand.end());
    }
    std::shuffle(unseenCards.begin(), unseenCards.end(), prng());
    auto u = unseenCards.begin();
    for (auto p : m_players){
        if (p == observer)
            continue;
        auto &hand = clone->m_playerCards[p];
        std::copy_n(u, hand.size(), hand.begin());
        u += hand.size();
    }
	return clone;
}

Zsir::Zsir(unsigned int players)
	: m_numPlayers(players)
{	
    for (unsigned j {0}; j < 8; ++j)
	for (unsigned i {0}; i < 4; ++i){
		m_deck[i*8+j] = { Card::Szin (i), Card::Kep (j) };
	}
    m_deckUsed = m_deck;
	m_players.resize(m_numPlayers);
	std::iota(m_players.begin(), m_players.end(), 0);
	m_playerCards.resize(m_numPlayers);
	m_scores.resize(m_numPlayers);
	deal();
}

Zsir::Player Zsir::currentPlayer() const {
	return m_player;
}

// TODO: elengedés, továbbütés hozzáadása
void Zsir::doMove(Card const move) {
	m_currentTrick.emplace_back(m_player, move);
	auto &hand = m_playerCards[m_player];
	auto const pos = std::find(hand.begin(), hand.end(), move);
	if (pos < hand.end())
		hand.erase(pos);
	else
		throw std::out_of_range("pos");
	m_player = nextPlayer(m_player);
	if (m_currentTrick.size() == m_numPlayers){
		finishRound();
    }
	if (m_playerCards[m_player].empty() &&
	    m_deckUsed.size() == 0)
		endGame();
	return;
}

double Zsir::getResult(Player player) const
{
	Card::Kep trump = m_currentTrick[0].second.kep;
	Player taker;
	
	auto i = m_currentTrick.end();
	while ( i != m_currentTrick.begin() ) {
		if ( (*i).second.kep == trump ||
		     (*i).second.kep == Card::VII){
			taker = (*i).first;
			break;
		}
		i--;
	}

	if (taker != player)
		return 0;

	return (double) trickValue();
}

int Zsir::trickValue(void) const {
	int score = 0;
	for (auto &play : m_currentTrick){
		Card::Kep kep = play.second.kep;
		if (!(kep == Card::ASZ || kep == Card::X))
			score += 1;
		else
			score += kep;
	}
	return score;
}

std::vector<Card> Zsir::validMoves() const {
	return m_playerCards[m_player];
}

void Zsir::finishRound() {
	Card::Kep trump = m_currentTrick[0].second.kep;
    // if no one attacked, the winner is the first person
	Player taker = 0;
	auto i = m_currentTrick.end();
	while (i != m_currentTrick.begin()){
		if ( (*i).second.kep == trump ||
		     (*i).second.kep == Card::VII){
			taker = (*i).first;
			break;
		}
		i--;
	}
	m_scores[taker] += trickValue();
	m_currentTrick.clear();
	// m_startingPlayer = taker;
    m_player = taker;
	deal();
}

// TODO
void Zsir::endGame() {
	finishRound();
	m_gameOver = true;
}

std::vector<Zsir::Player> Zsir::players() const {
	return m_players;
}

Zsir::Player Zsir::nextPlayer(Player p) const {
	return ++p % m_numPlayers;
}

void Zsir::AIMove(){
    ISMCTS::SOSolver<Card> solver;
    this->doMove(solver(*this));
}

std::ostream& operator<<(std::ostream &out, Zsir const &g)
{
	out << "Jatekosok kartyai:" << std::endl;
	for (unsigned int i = 0; i<g.m_numPlayers; i++){
		auto const &hand = g.m_playerCards[i];
		std::copy(hand.begin(), hand.end(), std::ostream_iterator<Card>(out, ","));
		out << std::endl;

	}
	out << "Pakli:" << std::endl;
	for (auto play : g.m_currentTrick)
		out << play.second << ", ";
	out << std::endl;
	return out;
}

#ifdef DEBUG
void Zsir::scoreTest(void) {

	Card testCards[] = { Card(Card::ZOLD,  Card::VIII),
			     Card(Card::PIROS, Card::VIII),
			     Card(Card::PIROS, Card::VII),
			     Card(Card::TOK,   Card::ASZ) };

	for (auto c : testCards)
		doMove(c);

	for (auto score : m_scores)
		std::cout << score << std::endl;
}

void Zsir::playTest(void) {
	for (auto pCards : m_playerCards){
		doMove(pCards[0]);
		std::cout << *this << std::endl;
	}
}

void Zsir::AITest(void) {
    for ( auto p : m_players ) {
        AIMove();    
        std::cout << *this << std::endl;
    }
}

#endif //DEBUG

int main(int argc, char *argv[])
{
	
	auto zsir = Zsir(4);		
	std::cout << zsir << std::endl;
#ifdef DEBUG
	// zsir.scoreTest();
	// zsir.playTest();
    zsir.AITest();
#endif //DEBUG
    std::cout << zsir << std::endl;

	return 0;
}
