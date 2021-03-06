import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from bokeh.plotting import figure, output_notebook, show
from bokeh.io import output_file, show, vplot
from bokeh.charts import HeatMap, output_file, show
from bokeh.models import NumeralTickFormatter
from bokeh.sampledata.autompg import autompg
from bokeh.charts import HeatMap, bins, output_file, show
from bokeh.models import HoverTool, BoxSelectTool
from bokeh import mpl
from bokeh.embed import components
import matplotlib.gridspec as gridspec

def extract_unique_mutations(df):
    df.columns = ['mutations', 'barcodes', 'brightness', 'std']
    df.mutations.fillna('', inplace=True)
    unique_mutations = set(':'.join(df.mutations.values).split(':'))
    unique_mutations.remove('')
    return unique_mutations

def result(infile):
    df = pd.DataFrame.from_csv(infile, sep = '\t', index_col=None)
    
    unique_mutations = extract_unique_mutations(df)    
    df['mut_number'] = df.mutations.apply(lambda x: x.count(':') + 1)

    # barcodes distribution
    hist, edges = np.histogram(df.brightness, density=False, bins=41)
    s1 = figure(width = 700, height = 500, title = 'Fitness distribution')
    s1.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
            fill_color="#FF5656", line_color="#033649", alpha = 0.7)
    s1.xaxis.axis_label = 'Fitness'
    
    # mutation distribution
    positions = [int(m[2:-1]) for m in unique_mutations if m != '']
    hist, edges = np.histogram(positions, density=False, bins=max(positions))
    s2 = figure(width = 900, height = 300, title = 'Mutations distribution')
    s2.quad(top = hist, bottom=0, left=edges[:-1], right=edges[1:],
            fill_color="#1C7293", line_color="#033649", alpha = 0.5)
    s2.xaxis.axis_label = 'Position number'
    s2.yaxis.axis_label = 'Number of mutations'
    
    # aminoacid switches
    aas = list("ACDEFGHIKLMNPQRSTVWYX*")
    aa2aa = pd.DataFrame(columns = aas, index = aas).fillna(0)
    for m in unique_mutations:
        aa2aa[m[-1]].ix[m[1]] += 1
    aa2aa = aa2aa.stack().reset_index()
    aa2aa.columns = ['From','To','num']
    s3 = HeatMap(data = aa2aa, x = 'To', y = 'From', values = 'num', stat = None,  legend=False, title = 'Aminoacid switches')

    # Number of unique mutations in different types of mutants
    uniques = []
    for i in range(max(df.mut_number)):
        subset = df[df.mut_number == i]
        uniques.append(len(set(':'.join(subset.mutations.values).split(':'))))
    s4 = figure(width = 900, height = 500, title = 'Mutations distribution', tools = [HoverTool(),'box_zoom,box_select,crosshair,resize,reset'])
    s4.line([x for x in range(max(df.mut_number))], uniques)
    s4.circle([x for x in range(max(df.mut_number))], uniques)
    s4.xaxis.axis_label = 'Mutant type'
    s4.yaxis.axis_label = 'Number of unique mutations'
    
    # Violin
    fig = plt.figure(figsize = [5,5])
    ax = {}
    gs1 = gridspec.GridSpec(4, 4)
    for num in range(1, 17):
        sns.set_style("whitegrid")
        ax[num] = fig.add_subplot(gs1[num-1])
        sns.violinplot(df.brightness[df.mut_number == num], linewidth = .5, color = '#57D1C9', orient = 'v', ax = ax[num])
        plt.xlabel('Number of mutations = %d' % num)
        plt.ylabel('Fitness', )
        plt.ylim(0,5)
    plt.subplots_adjust(left=None, bottom=None, right=1.8, top=1, wspace=None, hspace=None)
    s5 = mpl.to_bokeh()
    
    p = vplot(s1, s2, s3, s4, s5)
    script, div = components(p)
    return str(script),str(div)