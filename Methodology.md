# Methodology
<b> Description: </b> Novel techniques have shown Light Detection and Ranging (LiDAR) data can be used to highlight burial sites. Given the usefulness of LiDAR in the literature, we’re using this data to find unmarked graves in Jacksonville.

<b> Generally, our methodology will look as follows, and follow a RAG Methodology structure</b>
1. Understand what the elevation is - in Jacksonville, 
2. Account for density of agriculture
3. An account of historical churches/buildings

## RAG Methodology 
The Red-Amber-Green prioritization system is an approach that has been utilized in searches for graves and other buried objects for (decades)[https://pubs.geoscienceworld.org/gsl/books/edited-volume/1746/chapter-abstract/107630054/Geomorphological-and-geoforensic-interpretation-of?redirectedFrom=fulltext]. 


### Rag Table
|GIS-Based RAG Factor|Red Criterion|Amber Criterion|Green Criterion|Description|
|--------------------|-------------|---------------|---------------|-----------|
|Elevation|Elevation within 5th percentile|Elevation within 10th percentile|Elevation greater than 10th percentile|By using the elevation from LiDAR data we can filter to points with the lowest elev|
|Geomorpons|Slope/Foot Slope| Slope/Flat|Peak|Creating landforms called geomorphs can allow us to visualize microslopes in the ground. This may work better in a place like Florida where elevation changes are less drastic|
|Vegetation Density|Well-spaced trees/no dense vegetation|Sparsely dense vegetation|Dense vegetation|Using HLS 2 satelite data can allow us to classify vegetation|
|Historical Context|Within x feet of a church|Within x yards of a church|Within x miles of a church|The presence of a nearby church or heritage site may be indicative of a burial site in the area|