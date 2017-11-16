CREATE TABLE [dbo].[RelevantData](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[PK_DiagnosticDataSet] [int] NOT NULL,
	[FK_ReadOut] [int] NOT NULL,
	[FK_DiagnosticDataSetDefinition] [int] NOT NULL,
	[StartDateTime] [datetime] NULL,
	[EndDateTime] [datetime] NULL,
	[AckDateTime] [datetime] NULL,
	[Latitude] [float] NULL,
	[Longitude] [float] NULL,
	[DigitalSignalValues] [varchar](max) NULL,
	[AnalogSignalValues] [varchar](max) NULL,
	[DateTime] [datetime] NULL,
	[Description_L1] [nvarchar](200) NULL
)

  Insert Into [ConcertoDb_TIF_LAE_WA6463-65_26f6f855-fe1a-4d19-b233-59742ca93088].[dbo].[RelevantData]
  SELECT PK_DiagnosticDataSet, FK_ReadOut, FK_DiagnosticDataSetDefinition, StartDateTime, EndDateTime, AckDateTime, Latitude, Longitude, EnvironmentDataSet.DigitalSignalValues, EnvironmentDataSet.AnalogSignalValues, DateTime, DiagnosticDataSetDefinition.Description_L1
  FROM DiagnosticDataSet 
  JOIN DiagnosticDataSetDefinition ON (DiagnosticDataSet.FK_DiagnosticDataSetDefinition = DiagnosticDataSetDefinition.DefinitionNumber)
  JOIN EnvironmentDataSet ON (EnvironmentDataSet.FK_DiagnosticDataSet = DiagnosticDataSet.PK_DiagnosticDataSet)
  ORDER BY DiagnosticDataSet.StartDateTime