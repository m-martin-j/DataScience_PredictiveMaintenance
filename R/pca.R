library(devtools)
install_github("ggbiplot", "vqv")
library(ggbiplot)

# dinmerge_approx erstellt in korr_analyse2.R
#remove KranBetriebsstunden 3
dina<-dinmerge_approx[,-13] 


# apply PCA - scale. = TRUE is highly 
# advisable, but default is FALSE. 
din.pca <- prcomp(dina, center = TRUE, scale. = TRUE)

# Summary of PCA
print(din.pca)
summary(din.pca)
head(din.pca)
din.pca$rotation
write.csv(unclass(din.pca$rotation), file = "pca.csv")


#Visualize
plot(din.pca, type = "l")

#biplot(din.pca, scale = 0)
#g <- ggbiplot(din.pca, obs.scale = 1, var.scale = 1 , ellipse = TRUE, circle = TRUE)
#g <- g + scale_color_discrete(name = '')
#g <- g + theme(legend.direction = 'horizontal', legend.position = 'top')
#print(g)


