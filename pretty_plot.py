import matplotlib.pyplot as plot
import seaborn

plot.style.use('seaborn-v0_8')

def pretty_plot(functions, savefig = None, close = True):
    legend = []
    for args, kwargs, name in functions:
        legend.append(name)
        plot.plot(*args, **kwargs)

    if savefig is not None:
        plot.savefig(savefig[0], **savefig[1:])

    if close:
        plot.close()