library(RODBC)
library(corrplot)
library(Hmisc)
library(stringr)

dbhandle <- odbcDriverConnect('driver={SQL Server};server=localhost;database=ConcertoDb_DVT_WA6002_a4f12653-dd42-40f1-82c3-a6fdcf59fd4b;trusted_connection=true')

for (i in 2034:2034){
  print(paste("DinGroup", i))
  
  res <- sqlQuery(dbhandle, paste("SELECT AnalogSignalValues, DigitalSignalValues
    FROM [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet] 
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSetDefinition] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet].[FK_DiagnosticDataSetDefinition] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSetDefinition].[PK_DiagnosticDatasetDefinition])
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[EnvironmentDataSet] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[EnvironmentDataSet].[FK_DiagnosticDataSet] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet].[PK_DiagnosticDataSet])
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DinGroup] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DinGroup].[PK_DinGroup] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSetDefinition].[FK_DinGroup])
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[ReadOut] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet].[FK_ReadOut] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[ReadOut].[PK_ReadOut])
                  JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[Vehicle] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[ReadOut].[FK_Vehicle] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[Vehicle].[PK_Vehicle])
                  
                  WHERE PK_Vehicle = 2 AND PK_DinGroup =", i))
  
  
  formattedTable <- within(res, AnalogSignalValues<-data.frame(do.call('rbind', lapply(strsplit(as.character(AnalogSignalValues), ';', fixed=TRUE), as.numeric))))
  formattedTable <- within(formattedTable, DigitalSignalValues<-data.frame(do.call('rbind', lapply(strsplit(as.character(DigitalSignalValues), ';', fixed=TRUE), as.numeric))))
  
  colnames(formattedTable$AnalogSignalValues) <- paste("A", colnames(formattedTable$AnalogSignalValues), sep = "_")
  colnames(formattedTable$DigitalSignalValues) <- paste("D", colnames(formattedTable$DigitalSignalValues), sep = "_")
  
  correlationMatrix <- cor(formattedTable$AnalogSignalValues[1:9])
  
  corrplot(correlationMatrix, method="circle")
}

close(dbhandle)


