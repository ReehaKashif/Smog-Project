const calculateSourceContribution = async (district) => {
  let totalSourcesContributionValues = {};
  let totalSourcesContributionPercentages = {};

  const data = await getDistrictPollutantData(district);
  const totalPollutantsContributionValue = Object.values(
    data.pollutants
  ).reduce((acc, curr) => acc + curr, 0);

  // console.log("🔥", { totalPollutantsContributionValue });

  for (const source of pollutantsSources) {
    const sourcePollutantsContributionValue = calculatePollutantContribution(
      data.pollutants,
      source
    );

    // console.log("🔥🔥", { sourcePollutantsContributionValue });

    const sourceContributionPercentage = calculateSourceContributionPercentage(
      sourcePollutantsContributionValue,
      totalPollutantsContributionValue
    );

    totalSourcesContributionValues[source] = sourcePollutantsContributionValue;
    totalSourcesContributionPercentages[source] = sourceContributionPercentage;
  }

  return renderPollutantDataInTable(
    totalSourcesContributionValues,
    totalSourcesContributionPercentages
  );
};

const calculatePollutantContribution = (pollutants, source) => {
  let totalContribution = 0;

  for (const pollutant of pollutantsUnitsKeys) {
    let averageValue;
    const predictedValue = pollutants[pollutant];
    // console.log({ pollutantsUnitsKeys, predictedValue, pollutant, pollutants });
    const pollutantSymbol = pollutantsUnits[pollutant];
    // console.log({ pollutantSymbol });
    const averageSourceValue = pollutantsData[pollutantSymbol].sources[source];
    if (averageSourceValue.includes("-")) {
      const range = averageSourceValue.split("-").map(Number);
      averageValue = (range[0] + range[1]) / 2;
    } else {
      averageValue = Number(averageSourceValue);
    }

    const pollutantContribution = (predictedValue * averageValue) / 100;
    totalContribution += pollutantContribution;
  }
  // console.log({ totalContribution });
  return totalContribution;
};

const calculateSourceContributionPercentage = (
  sourceContribution,
  totalSourceContribution
) => {
  return (sourceContribution / totalSourceContribution) * 100;
};

const renderPollutantDataInTable = (
  totalSourcesContributionValues,
  totalSourcesContributionPercentages
) => {
  let tableData = [];
  let tableHtml =
    '<table class="pollutant-table w-[300px]"><thead class="p-2"><tr class="p-2"><th>Source</th><th>Value</th><th>%</th></tr></thead><tbody>';

  for (const source of pollutantsSources) {
    let sourceName = source === "Miscellaneous" ? "Misc" : source;
    tableData.push({
      source: sourceName,
      value: Math.round(totalSourcesContributionValues[source]),
      "%": Math.round(totalSourcesContributionPercentages[source]) + "%",
    });
  }

  // Sort tableData by value in descending order, but keep "Misc" last
  tableData.sort((a, b) => {
    if (a.source === "Misc") return 1; // Move Misc to the end
    if (b.source === "Misc") return -1; // Keep other sources before Misc
    return b.value - a.value; // Sort by value
  });

  // Generate HTML for sorted data
  for (const data of tableData) {
    tableHtml += `<tr class="p-2">
      <td>${data.source}</td>
      <td>${data.value}</td>
      <td>${data["%"]}</td>
    </tr>`;
  }

  // console.log("🔥🔥🔥", tableData[0].source);
  return {
    html: tableHtml,
    sourceWithHighestContribution: tableData[0].source,
  };
};

const getDistrictPollutantData = (district) => {
  return fetch(`${SERVER_URL}/current_pollutants?district=${district}`)
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .catch((err) => {
      console.error("Fetch error:", err);
      return null;
    });
};
