var dingroupValues = {};

dingroupValues["Allgemein (2034)"] = [
  "Dieselfüllstand [%]",
  "Frischwassertank [%]",
  "Batterie 1/2 Spannung [V]",
  "Batterie 3 Spannung [V]",
  "Batterie 4 Spannung [V]",
  "Batterie 1/2 Strom [A]",
  "Batterie 3 Strom [A]"
];

dingroupValues["Motor 1 (2035)"] = [
  "Drehzahl [U/min]",
  "Kühlmitteltemperatur [°C]",
  "Öldruck [1/10 bar]"
];

dingroupValues["Motor 2 (2036)"] = [
  "Drehzahl [U/min]",
  "Kühlmitteltemperatur [°C]",
  "Öldruck [1/10 bar]"
];

dingroupValues["Betriebsstunden (2037)"] = [
  "Betriebsstunden Motor 1 [h]",
  "Betriebsstunden Motor 2 [h]",
  "Betriebsstunden Kran 1 [h]",
  "Betriebsstunden Kran 2 [h]",
  "Betriebsstunden Kran 3 [h]"
];

dingroupValues["Hydraulik (2038)"] = [
  "Hydrauliköltank Füllstand [%]",
  "Hydrauliköl Temperatur [°C]"
];

dingroupValues["Getriebe Arbeitsfahrt (2039)"] = [
  "Fahrdruck A [bar]",
  "Fahrdruck B [bar]",
  "Speisedruck [bar]"
];

dingroupValues["Partikelfilter (2040)"] = [
  "Regeneration in [h]",
  "Filterwiderstand [mbar]",
  "Regenerationszeit [s]"
];

dingroupValues["Getriebe Überstellfahrt (2044)"] = [
  "Öltemperatur 1 [°C]",
  "Öltemperatur 2 [°C]",
  "Retarder 1 [%]",
  "Retarder 2 [%]",
  "Fahrdruck A [bar]",
  "Fahrdruck B [bar]",
  "Speisedruck [bar]"
];

dingroupValues["default"] = [];

for (var dingroup in dingroupValues) {
    if (dingroupValues.hasOwnProperty(dingroup)) {
        while(dingroupValues[dingroup].length < 9){
          dingroupValues[dingroup].push("Wert " + (dingroupValues[dingroup].length + 1));
        }
    }
}
