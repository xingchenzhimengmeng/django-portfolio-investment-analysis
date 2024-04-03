import akshare as ak
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def portfolio_variance(weights, cov_matrix):
    """
    计算组合方差
    """
    return np.dot(weights.T, np.dot(cov_matrix, weights))

def negative_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate):
    """
    计算夏普收益率
    """
    portfolio_return = np.sum(mean_returns * weights)
    portfolio_volatility = np.sqrt(portfolio_variance(weights, cov_matrix))
    return -(portfolio_return - risk_free_rate) / portfolio_volatility

def optimize_portfolio(mean_returns, cov_matrix, risk_free_rate):
    """
    Optimize portfolio allocation using scipy minimize
    """
    num_assets = len(mean_returns)
    initial_weights = np.array([1 / num_assets] * num_assets)  # Equal initial allocation

    # Constraints: weights sum up to 1
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})

    # Bounds: each weight should be between 0 and 1
    bounds = tuple((0, 1) for _ in range(num_assets))

    result = minimize(negative_sharpe_ratio, initial_weights,
                      args=(mean_returns, cov_matrix, risk_free_rate),
                      method='SLSQP', bounds=bounds, constraints=constraints)

    return result.x


def Portfolio_investment_analysis(codes):
    # codes = ['688631', '600519', '688631', '603219']
    code_list=[]
    data = []
    for code in codes:
        try:
            try:
                da = ak.stock_zh_index_daily_tx(symbol='sh' + code)
            except:
                da = ak.stock_zh_index_daily_tx(symbol='sz' + code)
            code_list.append(code)
            data.append(da)
        except:
            continue
    if len(code_list) < 2:
        return False
    num = min([len(da) for da in data])
    data = [da.iloc[-num::7]['close'].values for da in data]
    num = min([len(da) for da in data])
    print(num)
    for da in data:
        # print(len(da))
        for i in range(1, num):
            da[i-1] = (da[i]-da[i-1])/da[i-1]*100
    data = [da[:-1] for da in data]
    mean_returns = [np.mean(da) for da in data]
    cov_matrix = np.cov(np.array(data))
    print(mean_returns, cov_matrix)
    risk_free_rate = 0.025*7/254
    graphic = plot_efficient_frontier(mean_returns, cov_matrix, risk_free_rate)
    weights = optimize_portfolio(mean_returns, cov_matrix, risk_free_rate)
    # result = zip(code_list, weights)
    # print(code_list, weights)
    portfolio_return = np.sum(mean_returns * weights)
    s_variance = np.sqrt(portfolio_variance(weights, cov_matrix))
    weights = [round(weight, 3) for weight in weights]
    form = {
        'code_list': code_list,
        'mean_returns': mean_returns,
        'weights': weights,
        'portfolio_return': portfolio_return,
        'variance': s_variance,
        'graphic': graphic,
    }
    return form


def generate_random_portfolios(num_portfolios, mean_returns, cov_matrix, risk_free_rate):
    """
    Generate random portfolios with random weights
    """
    results = np.zeros((3, num_portfolios))  # Rows: return, volatility, Sharpe ratio

    for i in range(num_portfolios):
        weights = np.random.rand(len(mean_returns))
        weights /= np.sum(weights)  # Normalize to sum up to 1

        portfolio_return = np.sum(mean_returns * weights)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility

        results[0,i] = portfolio_return
        results[1,i] = portfolio_volatility
        results[2,i] = sharpe_ratio

    return results

def plot_efficient_frontier(mean_returns, cov_matrix, risk_free_rate, num_portfolios=10000):
    """
    Plot efficient frontier
    """
    portfolios = generate_random_portfolios(num_portfolios, mean_returns, cov_matrix, risk_free_rate)

    plt.figure(figsize=(10, 6))
    plt.scatter(portfolios[1,:], portfolios[0,:], c=portfolios[2,:], cmap='viridis', marker='o')
    plt.title('Efficient Frontier')
    plt.xlabel('Risk')
    plt.ylabel('Yield')
    plt.colorbar(label='Sharpe_rate')
    plt.grid(True)
    # plt.show()
    # 将图表转换为Base64编码的字符串
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    return graphic


def draw_k(code):
    # code = '603219'
    try:
        try:
            data = ak.stock_zh_index_daily_tx(symbol='sh' + code)
        except:
            data = ak.stock_zh_index_daily_tx(symbol='sz' + code)
    except:
        print("error")
        return False
    # 将日期列转换为Datetime类型并设置为索引
    print(data)
    # 转换日期格式为Matplotlib能够理解的格式
    data['date'] = data['date'].apply(mdates.date2num)
    ohlc = []
    for i in range(len(data['date'])):
        ohlc.append([data['date'][i], data['open'][i], data['high'][i], data['low'][i], data['close'][i]])

    # 设置图形大小和样式
    plt.figure(figsize=(12, 6))

    # 绘制K线图
    plt.style.use('seaborn-darkgrid')

    # 绘制K线
    plt.subplot(2, 1, 1)
    plt.title('K_image')
    plt.xlabel('date')
    plt.ylabel('price')
    candlestick_ohlc(plt.gca(), ohlc, width=0.6, colorup='r', colordown='g')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    # 绘制交易量柱状图
    plt.subplot(2, 1, 2)
    plt.title('amount')
    plt.xlabel('date')
    plt.ylabel('amount')
    plt.bar(data['date'], data['amount'], color='gray', alpha=0.3)

    plt.xticks(rotation=45)
    plt.tight_layout()
    # plt.show()
    # 将图表转换为Base64编码的字符串
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    return graphic
