def createLinearRegressionChart(dataset):
    data = dataset
    x = mdates.date2num(data.index.to_pydatetime())
    y = data['Price']

    slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
    line = slope*x+intercept
    trace1 = go.Scatter(
                    x=x,
                    y=y,
                    mode='markers',
                    marker=go.Marker(color='rgb(255, 127, 14)'),
                    name='Data'
    )
    trace2 = go.Scatter(
                    x=x,
                    y=line,
                    mode='lines',
                    marker=go.Marker(color='rgb(31, 119, 180)'),
                    name='Fit'
    )
    figData = [trace1, trace2]
    return plotly.offline.plot(figData, output_type='div', show_link=False, link_text=False)
    #m,b = np.polyfit(x, y, 1)

    #return (m,b)
