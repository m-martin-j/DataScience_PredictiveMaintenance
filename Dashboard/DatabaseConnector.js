const sql = require('mssql');
var config = require('./config');

function DatabaseConnector(){

  this.connectToDatabase = function(){
    return sql.connect(config.databaseConnection).then(connection => {
        console.log("Connected to Database!");
        this.connection = connection;
        return connection;
    }).catch(err => {
      console.error("Failed to connect to database!");
      console.error(err);
    });
  }

  this.selectAnalogValues = function(dinGroup, value, dateStart, dateEnd, includeZeros){
    if(!this.connection){
      return this.connectToDatabase().then(() => {return this.selectAnalogValues(dinGroup, value, dateStart, dateEnd, includeZeros)});
    }

    var includeZeroText = "";
    if(includeZeros != 'true'){
       includeZeroText = " AND AV" + value + " > 0";
    }
    console.log(typeof includeZeros);
    console.log(includeZeroText);

    return this.connection.request().query('SELECT DateTime, AV' + value + ' FROM AnalogValues2 WHERE AV' + value + ' < 5000 AND PK_DinGroup = ' + dinGroup + " AND DateTime BETWEEN CONVERT(datetime, '" + dateStart + "', 104) AND CONVERT(datetime, '" + dateEnd + "', 104)" + includeZeroText + " ORDER BY DateTime").then(result => {
      return result.recordsets[0].map((record) => {
        return {x: Date.parse(record["DateTime"]), y: parseInt(record["AV" + value])};
      });
    }).catch(err => console.log(err))
  }

  this.selectWarnings = function(includeInfos, includeWarnings, includeErrors, dateStart, dateEnd){
    if(!this.connection){
      return this.connectToDatabase().then(() => {return this.selectWarnings(includeInfos, includeWarnings, includeErrors, dateStart, dateEnd)});
    }

    var selectDingroups = "";
    if(includeInfos == "true"){
      selectDingroups += "OR PK_DinGroup = '2043' ";
    }
    if(includeWarnings == "true"){
      selectDingroups += "OR PK_DinGroup = '2042' ";
    }
    if(includeErrors == "true"){
      selectDingroups += "OR PK_DinGroup = '2041' ";
    }

    selectDingroups = "(" + selectDingroups.substring(3, selectDingroups.length - 1) + ")";

    return this.connection.request().query('SELECT DateTime, PK_DinGroup, Description FROM AnalogValues2 WHERE ' + selectDingroups + " AND DateTime BETWEEN CONVERT(datetime, '" + dateStart + "', 104) AND CONVERT(datetime, '" + dateEnd + "', 104) ORDER BY DateTime").then(result => {
      return result.recordsets[0].map((record) => {
        var type = "";
        switch(record["PK_DinGroup"]){
          case 2041:
            type = "Alarm";
            break;
          case 2042:
            type = "Warnung";
            break;
          case 2043:
            type = "Hinweis"
            break;
        }
        return [Date.parse(record["DateTime"]), type, record["Description"]];
      });
    }).catch(err => console.log(err))
  }

}

module.exports = new DatabaseConnector();
