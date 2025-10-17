Select *
From [PortfolioProject].[dbo].[netflix_titles$]

-- Finding different types of movies
Select Distinct type
From [PortfolioProject].[dbo].[netflix_titles$];

--15 Example Problems

-- 1. Count the number of movies and TV shows
Select type, COUNT(*) as total_content
From [PortfolioProject].[dbo].[netflix_titles$]
Group by type

-- 2. Find the most common rating for movies and TV shows
Select type, rating, COUNT(*) as total_rating, RANK() Over(PARTITION By type Order by COUNT(*) Desc) as ranking
From [PortfolioProject].[dbo].[netflix_titles$]
Group By type, rating

-- 3. List all the movies released in a specific year
Select *
From [PortfolioProject].[dbo].[netflix_titles$]
Where type = 'Movie' AND release_year = 2020

-- 4. Find the top 5 countries with the most content on Netflix 
Select TOP(5) COUNT(value) as Total_content, value
From [PortfolioProject].[dbo].[netflix_titles$]
cross apply STRING_SPLIT(country, ',') as new_country
Group By  value
Order By Total_content Desc

-- 5. Identify the longest movies
Select show_id, type, title, duration
From [PortfolioProject].[dbo].[netflix_titles$]
Where duration is not null and type = 'movie'
Order By duration DESC


-- 6. Find content added in the last 5 years
Select *
From [PortfolioProject].[dbo].[netflix_titles$]
Where date_added>= DATEADD(YEAR, -5, GETDATE())

-- 7. Find all the movies/TV shows by Steven Spielberg
Select *
From [PortfolioProject].[dbo].[netflix_titles$]
Where director = 'Steven Spielberg'

-- 8. List all TV shows with more than 5 seasons
Select show_id, title, type, duration
From [PortfolioProject].[dbo].[netflix_titles$] 
Where type = 'TV Show' and duration >= '5 seasons'

-- 9. Count the number of content items in each genre
Select value, COUNT(*)as total_content
From [PortfolioProject].[dbo].[netflix_titles$] 
Cross Apply STRING_SPLIT(listed_in, ',')
Group By value
Order by total_content Desc

-- 10. Find each year and the amount of content released in US to Netflix.
Select YEAR(date_added) as dateYear, COUNT(*) as YearCount
From [PortfolioProject].[dbo].[netflix_titles$] 
Where country = 'United States'
Group By YEAR(date_added)
Order By YEAR(date_added) DESC

-- 11. List all movies that are documentaries
Select *
From [PortfolioProject].[dbo].[netflix_titles$] 
Where listed_in like '%documentaries%'

-- 12. Find all content without a director
Select *
From [PortfolioProject].[dbo].[netflix_titles$] 
Where director is null

-- 13. Find how many movies a specific actor appeared in the last 10 years
Select *
From [PortfolioProject].[dbo].[netflix_titles$] 
Where cast like '%Anna Kendrick%'

-- 14. Find the top 20 actors who have appeared in the highest number of movies made in the United States
Select top 20(value), COUNT(*) as NUM_of_ACT
From [PortfolioProject].[dbo].[netflix_titles$] 
Cross Apply STRING_SPLIT(cast, ',')
Where country like '%United states%'
Group By value
Order By NUM_of_ACT DESC

/* 15. Categorize the content based on the presence of the key word 'kill' and 'violence' 
in the description field. Label content containing the key words as 'Danger' and all other
content as 'Safe'. Count how many items fall into each category. */
With New_table
as(
Select *,
	Case 
		When description LIKE '%violence%' or description LIKE '%kill%' THEN 'DANGER' 
		ELSE 'Safe'
	END Category
From [PortfolioProject].[dbo].[netflix_titles$] 
)
Select Category, COUNT(*) as total_content
From New_table
Group By Category
