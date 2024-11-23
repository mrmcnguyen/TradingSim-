
import market
def get_portfolio_details(portfolio):

    # Calculate total portfolio value
    for stock in portfolio:
        portfolioValue += stock[1] * market.get_ticker_price(stock[3])

    # Calculate P&L
    for stock in portfolio:
        current_price = market.get_ticker_price(stock[0])
        stock.append(round(current_price - stock[3], 2)*stock[1] if current_price > stock[3] else round(-(stock[3] - current_price),2)*stock[1] if current_price < stock[3] else 0)

    #Calculate total P&L
    for stock in portfolio:
        PandL += stock[4]

    #Calculate current portfolio value
    for stock in portfolio:
        stock.append(stock[1] * market.get_ticker_price(stock[3]))

    #Calculate percentage change
    for stock in portfolio:
        stock.append(round((stock[5] - stock[2])/100, 2) if stock[5] > stock[2] else round(-(stock[2] - stock[5])/100, 2) if stock[2] > stock[5] else 0)
    
    #Calculate total percentage change
    for stock in portfolio:
        percentageChange += stock[6]