from shiny import App, render, ui, reactive
from os import listdir
from os.path import isfile, join
from datetime import datetime

import requests
import json
import re

import numpy as np
import os, shutil
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import random


debug = 1

graphList = ["Conventional Power Generation", "Power Generation", "Power Export-Import"]

with open("energyData-Scraper/shinyApp/app/data/conventional_power_generation_30.04.2023-31.05.2023.json") as f:
    convPowGen = f.read()

with open("energyData-Scraper/shinyApp/app/data/power_generation_30.04.2023-31.05.2023.json") as f:
    powGen = f.read()

with open("energyData-Scraper/shinyApp/app/data/power_import_export_30.04.2023-31.05.2023.json") as f:
    powImportExport = f.read()

graphDicts = [convPowGen, powGen, powImportExport]

app_ui = ui.layout_sidebar(
    ui.panel_sidebar(
        #ui.h2("Hello Shiny!"),
        #ui.input_slider("n", "N", 0, 100, 20),
        #ui.output_text_verbatim("txt"),

        ui.input_selectize("selz_graphsToFetch", "Graphs to fetch (multiple)", graphList, multiple = True),
        ui.output_text_verbatim("txt_graphsToFetch"),
        ui.input_date_range("dateRange_scope", "Date range input", format="dd.mm.yyyy",  start="2023-04-30", end="2023-05-03"),
        ui.p(ui.input_action_button("btn_fetch", "Fetch Data!")),
        ui.h2("Available graphs:"),
        ui.input_select("sel_graphs", "Available graphs (multiple)",choices=[], multiple = True),
        ui.p(ui.input_action_button("btn_update", "Update!")),
        ui.output_text_verbatim("txt_graphsAvail"),

        ui.h2("Available series:"),
        ui.input_select("sel_series", "Available primary series (multiple)",choices=[], multiple = True),
        ui.output_text_verbatim("txt_seriesAvail"),

        ui.input_select("sel_seriesSec", "Available secondary series (multiple)",choices=[], multiple = True),
        ui.output_text_verbatim("txt_seriesAvailSec"),

        ui.p(ui.input_action_button("btn_update_series", "Update!")),

        ui.p(ui.input_action_button("btn_graph", "Graph!")),
    ),
    ui.panel_main(
        ui.output_plot(id="outputPlot",
                       width="100%",
                       height="600px",
                       click=False,
                       dblclick=False,
                       hover=False,
                       brush=False,
                       inline=False,)

    )
)


def server(input, output, session):
    graphFiles = reactive.Value([])
    graphFilesNames = reactive.Value([])
    dateFrom = reactive.Value(0)
    dateUntil = reactive.Value(0)
    dateFromStr = reactive.Value(0)
    dateUntilStr = reactive.Value(0)
    graphSeries = reactive.Value([])
    graphReady = reactive.Value(0)


    @output
    @render.text
    def txt():
        return f"n*2 is {input.n() * 2}"
    
    @output
    @render.text
    def txt_graphsAvail():
        return input.sel_graphs.get()
    
    @output
    @render.text
    def txt_seriesAvail():
        return input.sel_series.get()
    
    @output
    @render.text
    def txt_seriesAvailSec():
        return input.sel_seriesSec.get()

    @output
    @render.text
    def txt_graphsToFetch():
        return input.selz_graphsToFetch.get()
    
    #@output
    #def fetchStartDate():

    @reactive.Effect
    @reactive.event(input.btn_graph)
    def graph():
        graphReady.set(True)
        """
        #get selected series
        graphSers = graphSeries.get()
        time = graphSers[0]
        primarySeries = graphSers[1]
        secondarySeries = graphSers[2]
        emissions_intensity = graphSers[3]
        for serie in primarySeries:
            if serie not in input.sel_series.get():
                primarySeries.pop(serie)

        for serie in secondarySeries:
            if serie not in input.sel_seriesSec.get():
                secondarySeries.pop(serie)

        if "emissions_intensity" not in input.sel_seriesSec.get():
            emissions_intensity = []

        #Insert matplotlib plot
        """
        
        """
        # Data for plotting
t = np.arange(0.0, 2.0, 0.01)
s = 1 + np.sin(2 * np.pi * t)

fig, ax = plt.subplots()
ax.plot(t, s)

ax.set(xlabel='time (s)', ylabel='voltage (mV)',
       title='About as simple as it gets, folks')
ax.grid()

fig.savefig("test.png")
plt.show()
        
        """

    @output
    @render.plot
    def outputPlot():
        #get selected series
        graphSers = graphSeries.get()

        if graphReady.get() != True: #Show default graph
            return
            # Data for plotting
            t = np.arange(0.0, 2.0, 0.01)
            s = 1 + np.sin(2 * np.pi * t)

            fig, ax = plt.subplots()
            ax.plot(t, s)

            ax.set(xlabel='time (s)', ylabel='voltage (mV)',
                title='About as simple as it gets, folks')
            ax.grid()
            return fig
        else:
            
            time = graphSers[0]
            if isinstance(time[0],int):
                for idx_item, timeVal in enumerate(time):
                    ts = timeVal /1000
                    time[idx_item] = datetime.fromtimestamp(ts)

            primarySeries = {} #graphSers[1]
            secondarySeries = {} #graphSers[2]
            emissions_intensity = graphSers[3]
            plotColors = []#graphSers[4] 
            for serie, values in graphSers[1].items():
                if serie in input.sel_series.get():
                    primarySeries[serie] = values

            for serie, values in graphSers[2].items():
                if serie in input.sel_seriesSec.get():
                    secondarySeries[serie] = values

            if "emissions_intensity" not in input.sel_seriesSec.get():
                emissions_intensity = []
            #Insert matplotlib plot

            #plotSeries = []
            #for country in plotCountries:
            #    plotSeries.append(typesEmissions['Total'][country])

            for serie in primarySeries:
                plotColors.append(graphSers[4][serie])

            fig, ax = plt.subplots()

            ax.stackplot(time,primarySeries.values(), labels=primarySeries.keys(), colors = plotColors)
            ax.set_xlabel('DateTime')
            ax.set_ylabel('Power generation and consumption (Gw)')
            ax.set_title('Power generation and consumption')
            #ax.legend(loc='center right', bbox_to_anchor=(6.0, 0.55), ncol=10, fancybox=True, shadow=True)

            # get handles and labels for reuse
            ax.set_xticklabels(ax.get_xticks(), rotation = 45)
            label_params = ax.get_legend_handles_labels()
            ax.legend(*label_params,
                      loc='upper left', bbox_to_anchor=(0.25, -0.5), ncol=2, fancybox=True, shadow=True, prop={"size":8})
            #plt.tight_layout()
            #plt.show()

            if len(secondarySeries) >=1:
                plt.twinx()
                secSeries = []
                for serie in secondarySeries.values():
                    secSeries.append(serie)
                coo = plt.plot(time, secSeries[0], color='blue')
                plt.ylabel('Co2 Kg')

            return fig

    @reactive.Effect
    @reactive.event(input.btn_update_series)
    def getAvailSeries():
        graphReady.set(False)
        graphsDir = "energyData-Scraper/shinyApp/app/data/graphs/"
        
        selGraphsDictList = []
        for graph in input.sel_graphs.get():
            graphDict = json.load(open(join(graphsDir,f"{graph}.json")))
            selGraphsDictList.append(graphDict)
        
        time = []
        emissions_intensity = []
        primarySeries = {}
        secondarySeries = {}
        plotColors = {}
        for graphDict in selGraphsDictList:
            for serie in graphDict.keys():
                if serie == "time":
                    time = graphDict[serie]
                    continue
                if serie == "emission_intensity":
                    emissions_intensity = graphDict[serie]
                    continue
                if serie in ["period"]: continue
                if serie in ["emission_co2", "total_load", "balance", "sum_import_export", "power_price"]:
                    secondarySeries[serie] = graphDict[serie]
                    continue
                primarySeries[serie] = graphDict[serie]

        for graphDict in selGraphsDictList:
            for serie in graphDict.keys():
                match serie:
                    case "solar":
                        plotColors[serie] = "yellow"
                    case "wind_onshore":
                        plotColors[serie] = "skyblue"
                    case "wind_offshore":
                        plotColors[serie] = "deepskyblue"
                    case "run_of_the_river":
                        plotColors[serie] = "aqua"
                    case "biomass":
                        plotColors[serie] = "forestgreen"
                    case "hydro_pumped_storage":
                        plotColors[serie] = "cornflowerblue"
                    case "gas":
                        plotColors[serie] = "darkgrey"
                    case "coal":
                        plotColors[serie] = "dimgrey"
                    case "lignite":
                        plotColors[serie] = "darkslategrey"
                    case "uranium":
                        plotColors[serie] = "springgreen"
                    case "other":
                        plotColors[serie] = "fuchsia"
                    case _:
                        colorName, colorCode = random.choice(list(mcolors.CSS4_COLORS.items()))
                        plotColors[serie] = colorName
                pass

        for idx_item, timeVal in enumerate(time):
                    ts = timeVal /1000
                    time[idx_item] = datetime.fromtimestamp(ts)

        graphSeries.set([
            time,
            primarySeries,
            secondarySeries,
            emissions_intensity, 
            plotColors
        ])

        primSeriesNames = [serieName for serieName in primarySeries.keys()]
        ui.update_select(id="sel_series", choices=primSeriesNames)

        secSeriesNames = [serieName for serieName in secondarySeries.keys()]
        ui.update_select(id="sel_seriesSec", choices=secSeriesNames)


    @reactive.Effect
    @reactive.event(input.btn_update)
    def getAvailGraphs():
        graphReady.set(False)
        graphsDir = "energyData-Scraper/shinyApp/app/data/graphs/"
        graphFiles.set([f for f in listdir(graphsDir) if isfile(join(graphsDir, f))])
        graphFNames = []
        for graphFile in graphFiles.get():
            posStart, posEnd = graphFile.rfind("/"), graphFile.rfind(".")
            graphFNames.append(graphFile[posStart+1:posEnd])
        #graphFNames.append(dateFromStr.get())
        #graphFNames.append(dateUntilStr.get())
        graphFilesNames.set(graphFNames)
        ui.update_select(id="sel_graphs", choices=graphFilesNames.get())

    @reactive.Effect
    @reactive.event(input.btn_fetch)
    def fetchData():
        graphReady.set(False)
        dateF, dateU = input.dateRange_scope.get()
        dateFrom.set(dateF)
        dateUntil.set(dateU)
        dateFromStr.set(dateF.strftime("%d.%m.%Y"))
        dateUntilStr.set(dateU.strftime("%d.%m.%Y"))
        period = {
            "start": dateF.strftime("%Y-%m-%d"),
            "end": dateU.strftime("%Y-%m-%d")
        }
        graphsToFetch = []
        if "Power Generation" in input.selz_graphsToFetch.get(): graphsToFetch.append("power_generation")
        if "Conventional Power Generation" in input.selz_graphsToFetch.get(): graphsToFetch.append("conventional_power_generation")
        if "Power Export-Import" in input.selz_graphsToFetch.get(): graphsToFetch.append("power_import_export")

        fetchParam = {
            "graph":{
                "power_generation": {
                    "missingChars": [
                        (1323, "}"),
                        (1102, "}")
                    ]
                },
                "conventional_power_generation": {
                    "missingChars": [
                        (1342, "}"),
                        (1111, "}")
                    ]
                },
                "power_import_export": {
                    "missingChars": [
                        (1625, "}"),
                        (1497, "}")
                    ]
                }
            }
        }

        #Clear graphs dir contents
        graphsDir = "energyData-Scraper/shinyApp/app/data/graphs/"
        logsDir = "energyData-Scraper/shinyApp/app/data/logs/"
        dirs = [graphsDir, logsDir]
        #folder = '/path/to/folder'
        for wkDir in dirs:
            for filename in os.listdir(wkDir):
                file_path = os.path.join(wkDir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))

        rawCharts = {}
        for chart in graphsToFetch:
            url = f"https://www.agora-energiewende.de/en/service/recent-electricity-data/chart/data/{chart}/{dateFromStr.get()}/{dateUntilStr.get()}/today/chart.json"
            data = requests.get(url)
            with open(join(logsDir, f"{chart}_log.txt"), "w") as f:
                f.write(url)
            parsed_data = json.loads(data.text)

            with open(join(logsDir, f"{chart}_log.txt"), "a") as f:
                f.write(data.text)

            if debug >=2:
                print(f"parsed_data ({type(parsed_data)}): {parsed_data}")
                with open("parsed_data.json","w") as f:
                    f.write(json.dumps(parsed_data, indent=4))

            jsonStr = json.dumps(parsed_data["js"], indent=4)
            if debug >=2:  print(f"jsonStr ({type(jsonStr)}): {jsonStr}")

            chartStatementStartPos = jsonStr.find("new Highcharts.chart(")
            chartStatementFuncStartPos = jsonStr.find("return {",chartStatementStartPos)
            jsonStrStartPos = chartStatementFuncStartPos + 7
            jsonStrEndPos = jsonStr.rfind("()") -2

            jsonIStr = jsonStr[jsonStrStartPos:jsonStrEndPos]
            if debug >=2: print(f"jsonIStr ({type(jsonIStr)}): {jsonIStr}")
            outputStr = jsonIStr#.replace("\\","")

            removeJSFuncs = True
            if removeJSFuncs:
                jsFuncFinder = re.compile('function\(\) \{.*?\}')
                funcPos = []
                for m in jsFuncFinder.finditer(outputStr):
                    funcPos.append(m.span())
                funcPos.reverse()

                if debug >=2: print(f"positions of the JS funcs to remove:\n{funcPos}")

                for pos in funcPos:
                    outputStr = outputStr[:pos[0]] + '"here was a JS function"' + outputStr[pos[1]+1:]

            removeHTMLTags = True
            if removeHTMLTags:
                htmlTagFinder = re.compile("<.*?>")
                htmlTagPos = []
                for m in htmlTagFinder.finditer(outputStr):
                    htmlTagPos.append(m.span())
                htmlTagPos.reverse()

                if debug >=2: print(f"positions of the html tags to remove:\n{htmlTagPos}")

                for pos in htmlTagPos:
                    outputStr = outputStr[:pos[0]] + outputStr[pos[1]:]

            removeVariableNames = True
            if removeVariableNames:
                varNameFinder = re.compile(':\s*(?!false|true)[a-zA-Z\.]+\s*(,|\})')
                variableNamePos = []
                for m in varNameFinder.finditer(outputStr):
                    variableNamePos.append(m.span())
                variableNamePos.reverse()

                if debug >=2: print(f"positions of the variable names to remove:\n{variableNamePos}")

                for pos in variableNamePos:
                    outputStr = outputStr[:pos[0]+1] + '"removed"' + outputStr[pos[1]-1:]

            removeExtraSlashes = True
            if removeExtraSlashes:
                outputStr = outputStr.replace('\\"', '"')
                if debug >=2: print(outputStr)

            addMissingChars = True
            if addMissingChars:
                #Missing character missingChar[1] at position missingChar[0] 
                for missingChar in fetchParam["graph"][chart]["missingChars"]:
                    outputStr = outputStr[:missingChar[0]-1] + missingChar[1] + outputStr[missingChar[0]-1:]
            with open(join(logsDir, f"{chart}.json"), "w") as f:
                f.write(outputStr)

            rawCharts[chart] = json.loads(outputStr)

        for chart in graphsToFetch:
            series = {}
            #print(f"graphDict ({type(graphDict)}): {rawCharts[chart]}")
            for serie in rawCharts[chart]["series"]:
                if "id" not in serie: continue
                if "name" in serie: 
                    if serie["name"] == "timeline": continue
                serieName = serie["id"].replace("-", "_")
                if debug >=2: print(f"serieName: {serieName}")
                rows = serie["data"]
                cols = np.array(rows).T.tolist()
                time = cols[0]
                series["time"] = time
                exec(serieName + "= cols[1]")
                #with open(join(logsDir, f"{chart}_log.txt"), "a") as f:
                #    f.write(f"str(globals().keys())\n{globals().keys()}\n\nstr(locals().keys())\n{locals().keys()}")
                series[serieName] = locals()[serieName]

            series["period"] = period


            with open(join(graphsDir,f"{chart}.json"),"w") as f:
                f.write(json.dumps(series,indent=4))

        #Update available graphs
        #getAvailGraphs():
        graphsDir = "energyData-Scraper/shinyApp/app/data/graphs/"
        graphFiles.set([f for f in listdir(graphsDir) if isfile(join(graphsDir, f))])
        graphFNames = []
        for graphFile in graphFiles.get():
            posStart, posEnd = graphFile.rfind("/"), graphFile.rfind(".")
            graphFNames.append(graphFile[posStart+1:posEnd])
        graphFilesNames.set(graphFNames)
        ui.update_select(id="sel_graphs", choices=graphFilesNames.get())

        




app = App(app_ui, server)
