def plotly_3d(df, filename, x_label='x', y_label='y', z_label='z', groupby=None,
              size=5, marker=None, title=None, width=1500, height=1000,
              sizeby=None, size_multiplier=100, leg_labels=None, legend=True):
    from plotly import graph_objs as go
    from plotly.offline import plot
    from bokeh import palettes
    from sklearn.preprocessing import MinMaxScaler
    import pandas as pd

    scaler = MinMaxScaler()

    def build_hover_text(data):
        labels = data.columns
        labels = [x for x in labels if x not in ['x', 'y']]
        base = data[labels[0]].apply(lambda x: '{}: {}'.format(labels[0], x))

        for label in labels[1:]:
            if type(data[label].iloc[0]) is list:
                fixed_data = data[label].apply(lambda x: ', '.join(x))
                base = base + '<br>' + '{}: '.format(label) + fixed_data
            else:
                base = base + '<br>' + '{}: '.format(label) + data[label].astype(str)

        return base

    def build_cluster_colors(local_labels):
        label_series = pd.Series(local_labels)
        str_labels = pd.Series(local_labels).unique()
        if len(str_labels) > 20:
            palette = palettes.viridis(len(str_labels))
        elif len(str_labels) < 3:
            palette = palettes.brewer['Set1'][3]
        else:
            palette = palettes.d3['Category20'][len(str_labels)]
        labels_int_lookup = {k: palette[i] for (i, k) in enumerate(str_labels)}
        graph_colors = label_series.apply(lambda x: labels_int_lookup[x]).tolist()
        return graph_colors

    traces = []
    if groupby is None:
        if sizeby is not None:
            size = scaler.fit_transform(df[[sizeby]]) * size_multiplier
        trace = go.Scatter3d(
            x=df[x_label],
            y=df[y_label],
            z=df[z_label],
            mode='markers',
            name=None,
            hovertext=build_hover_text(df),
            hoverinfo=('name+text'),
            marker=dict(size=size, color='blue') if marker is None else marker
        )
        traces.append(trace)
    else:
        groups = df.groupby(groupby)
        cluster_labels = df[groupby].unique()
        colors = build_cluster_colors(df[groupby].unique())
        for i, x in enumerate(cluster_labels):
            subset = groups.get_group(x)
            if sizeby is not None:
                size = scaler.fit_transform(subset[[sizeby]]) * size_multiplier
            trace = go.Scatter3d(
                x=subset[x_label],
                y=subset[y_label],
                z=subset[z_label],
                name='{}'.format(x) if leg_labels is None else '{} {}'.format(x, leg_labels[x]),
                mode='markers',
                hovertext=build_hover_text(subset),
                hoverinfo=('name+text'),
                marker=dict(size=size, color=colors[i]) if marker is None else marker
            )
            traces.append(trace)

    layout = go.Layout(
        title=title,
        autosize=True,
        width=width,
        height=height,
        hovermode='closest',
        yaxis=dict(zeroline=False),
        xaxis=dict(zeroline=False),
        showlegend=legend,
        margin=go.Margin(
            l=50,
            r=50,
            b=100,
            t=100,
            pad=4
        ))
    fig = go.Figure(data=traces, layout=layout)
    plot(fig, filename=filename if filename.endswith('.html') else filename + '.html')