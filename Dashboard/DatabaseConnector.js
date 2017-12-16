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

  this.selectAnalogValues = function(dinGroup, value, dateStart, dateEnd){
    if(!this.connection){
      return this.connectToDatabase().then(() => {return this.selectAnalogValues(dinGroup, value, dateStart, dateEnd)});
    }

    return this.connection.request().query('SELECT DateTime, AV' + value + ' FROM AnalogValues2 WHERE PK_DinGroup = ' + dinGroup + " AND DateTime BETWEEN CONVERT(datetime, '" + dateStart + "', 104) AND CONVERT(datetime, '" + dateEnd + "', 104) AND AV" + value + " != 0 ORDER BY DateTime").then(result => {
      return result.recordsets[0].map((record) => {
        return {x: Date.parse(record["DateTime"]), y: parseInt(record["AV" + value])};
      });
    }).catch(err => console.log(err))
  }

}

module.exports = new DatabaseConnector();
