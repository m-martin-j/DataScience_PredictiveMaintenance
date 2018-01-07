library(zoo)
library(corrplot)

# Lineare Approximation der fehlenden Werte

dinmerge_approx <- na.approx(dinmerge[,2:29], rule=2)

# Berechne Korrelationen 

cor(dinmerge_approx)


correlationMatrix <- cor(dinmerge_approx)

corrplot(correlationMatrix, method="circle")

summary(dinmerge$`Betriebsstund. Kran3`)
correlationMatrix

correlationMatrix34 <- cor(din2035[,1:3])

write.csv("corr.csv", correlationMatrix)

write.csv(correlationMatrix, file="cor.csv")

correlationMatrix34 <- cor(din2034[,1:2])
correlationMatrix36 <- cor(din2036[,1:3])
correlationMatrix37 <- cor(din2037[,1:5])
correlationMatrix38 <- cor(din2038[,1:2])
correlationMatrix39 <- cor(din2039[,1:3])
correlationMatrix40 <- cor(din2040[,1:3])
correlationMatrix44 <- cor(din2044[,1:7])



#### Interpolation und Korrelation auf Basis der zeitlich zusammengefassten Werte (1 Minute)

dinmerge_approx2 <- na.approx(dinmerge_round1m_sum[,2:29], rule=2)
correlationMatrix2 <- cor(dinmerge_approx2)
write.csv(correlationMatrix2, file="cor2.csv")


