# Stored variables, necessary for each ML approach


def get_sql_join(db,vehicle_nbr):
    # SQL query that executes relevant joins, not containing SELECT statement
    sql_part_routine =  """FROM ["""+db+"""].[dbo].[DiagnosticDataSet] 
                      JOIN ["""+db+"""].[dbo].[DiagnosticDataSetDefinition] ON (["""+db+"""].[dbo].[DiagnosticDataSet].[FK_DiagnosticDataSetDefinition] = ["""+db+"""].[dbo].[DiagnosticDataSetDefinition].[PK_DiagnosticDatasetDefinition])
                      JOIN ["""+db+"""].[dbo].[EnvironmentDataSet] ON (["""+db+"""].[dbo].[EnvironmentDataSet].[FK_DiagnosticDataSet] = ["""+db+"""].[dbo].[DiagnosticDataSet].[PK_DiagnosticDataSet])
                      JOIN ["""+db+"""].[dbo].[DinGroup] ON (["""+db+"""].[dbo].[DinGroup].[PK_DinGroup] = ["""+db+"""].[dbo].[DiagnosticDataSetDefinition].[FK_DinGroup])
                      JOIN ["""+db+"""].[dbo].[ReadOut] ON (["""+db+"""].[dbo].[DiagnosticDataSet].[FK_ReadOut] = ["""+db+"""].[dbo].[ReadOut].[PK_ReadOut])
                      JOIN ["""+db+"""].[dbo].[Vehicle] ON (["""+db+"""].[dbo].[ReadOut].[FK_Vehicle] = ["""+db+"""].[dbo].[Vehicle].[PK_Vehicle])
                      WHERE ReadOut.FK_Vehicle = """+vehicle_nbr
    
    return sql_part_routine