/****** Skript für SelectTopNRows-Befehl aus SSMS ******/
SELECT FK_ReadOut, StartDateTime, EndDateTime, AlarmCount, Latitude, Longitude, DiagnosticDataSetDefinition.Description_L1, EnvironmentDataSet.DigitalSignalValues, EnvironmentDataSet.AnalogSignalValues, DinGroup.Description_L1
  FROM DiagnosticDataSet 
  JOIN DiagnosticDataSetDefinition ON (DiagnosticDataSet.FK_DiagnosticDataSetDefinition = DiagnosticDataSetDefinition.PK_DiagnosticDatasetDefinition)
  JOIN EnvironmentDataSet ON (EnvironmentDataSet.FK_DiagnosticDataSet = DiagnosticDataSet.PK_DiagnosticDataSet)
  JOIN DinGroup ON (DinGroup.PK_DinGroup = DiagnosticDataSetDefinition.FK_DinGroup)
  ORDER BY DiagnosticDataSet.StartDateTime
