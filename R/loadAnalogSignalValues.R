library(RODBC)
library(corrplot)
library(Hmisc)
library(stringr)

dbhandle <- odbcDriverConnect('driver={SQL Server};server=localhost;database=ConcertoDb_DVT_WA6002_a4f12653-dd42-40f1-82c3-a6fdcf59fd4b;trusted_connection=true')
res <- sqlQuery(dbhandle, 'SELECT TOP (3) AnalogSignalValues
  FROM [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet] 
                JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSetDefinition] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet].[FK_DiagnosticDataSetDefinition] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSetDefinition].[PK_DiagnosticDatasetDefinition])
                JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[EnvironmentDataSet] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[EnvironmentDataSet].[FK_DiagnosticDataSet] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet].[PK_DiagnosticDataSet])
                JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DinGroup] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DinGroup].[PK_DinGroup] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSetDefinition].[FK_DinGroup])
                JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[ReadOut] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[DiagnosticDataSet].[FK_ReadOut] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[ReadOut].[PK_ReadOut])
                JOIN [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[Vehicle] ON ([ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[ReadOut].[FK_Vehicle] = [ConcertoDb_TIF_WA6358_59_b9500bbf-f52a-474a-92c5-b863ed31d004].[dbo].[Vehicle].[PK_Vehicle])
                
                WHERE PK_Vehicle = 2 AND PK_DinGroup = 34')


formattedTable <- within(res, AnalogSignalValues<-data.frame(do.call('rbind', strsplit(as.character(AnalogSignalValues), ';', fixed=TRUE))))
print(formattedTable)

#matrix <- data.matrix(formattedTable, rownames.force = NA)
#matrix <- matrix(as.numeric(unlist(formattedTable)),nrow=nrow(formattedTable))
#matrix <- as.matrix(sapply(unlist(formattedTable), as.numeric))
#matrix <- as.matrix(as.data.frame(lapply(formattedTable, as.numeric)))
#print(rcorr(matrix)[[1]])
#corrplot(res, method="circle")


close(dbhandle)

