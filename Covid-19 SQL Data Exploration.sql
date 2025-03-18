SELECT *
From PortfolioProject..CovidDeaths$
Where continent is not null
order by 3,4

--Selecting which data to use
Select Location, Date, Total_cases,New_cases, Total_deaths, Population
From PortfolioProject..CovidDeaths$
order by 1,2

--Looking at Total Cases vs Total Deaths (This shows the liklihood of dying if you get covid in your country)
Select Location, Date, Total_cases, Total_deaths, (Total_deaths/Total_cases)*100 as DeathPercentage
From PortfolioProject..CovidDeaths$
Where continent is not null
order by 1,2

-- Total cases vs Population (shows what perceentrage of each population gets covid)
Select Location, date, total_cases, population, (total_cases/population)*100 as PercentofPupulationInected
From PortfolioProject..CovidDeaths$
Where continent is not null
order by 1,2

-- Looking at countries with the highest infection rates compared to their population
Select Location, MAX(total_cases) as HighestInfectionCount, population, Max((total_cases/population))*100 as PercentofPopulationInected
From PortfolioProject..CovidDeaths$
-- location like'%states%'
Group by Location, population
order by PercentofPopulationInected desc

--Showing countries with the highest death count per population
Select Location, MAX(cast(Total_deaths as int)) as TotalDeathCount
From PortfolioProject..CovidDeaths$
-- location like'%states%'
Where continent is not null
Group by Location, population
order by TotalDeathCount desc

--Breakdown by continent
Select location, MAX(cast(Total_deaths as int)) as TotalDeathCount
From PortfolioProject..CovidDeaths$
--location like'%states%'
Where continent is not null
Group by location
order by TotalDeathCount desc


-- Global Numbers
Select  SUM(new_cases)as total_cases,SUM(cast(new_deaths as int))as total_deaths,
 SUM(cast(new_deaths as int))/SUM(new_cases)*100 as DeathPercentage
From PortfolioProject..CovidDeaths$
Where continent is not null
--Group by date
order by 1,2

-- Looking at total population vs vaccinations (With created view)
Create View TotalPopvsVaccination as
Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations, 
 SUM(CONVERT(int,vac.new_vaccinations)) OVER (Partition by dea.Location Order by 
 dea.Location, dea.Date) as RollingPeopleVaccinated
From PortfolioProject..CovidDeaths$ dea
Join PortfolioProject..CovidVaccinations$ vac
	on dea.location = vac.location
	and dea.date = vac.date
Where dea.continent is not null
--order by 2,3

-- USE CTE
With PopvsVac (Continent, Location, Date, Population, new_vaccinations, RollingPeopleVaccinated)
as
(
Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations, 
 SUM(CONVERT(int,vac.new_vaccinations)) OVER (Partition by dea.Location Order by 
 dea.Location, dea.Date) as RollingPeopleVaccinated
From PortfolioProject..CovidDeaths$ dea
Join PortfolioProject..CovidVaccinations$ vac
	on dea.location = vac.location
	and dea.date = vac.date
Where dea.continent is not null)

Select*, (RollingPeopleVaccinated/Population)*100
From PopvsVac

-- TEMP Table
DROP table if exists #PercentPopulationVaccinated
Create Table #PercentPopulationVaccinated
(
Continent nvarchar(255),
Location nvarchar(255),
Date datetime,
Population numeric,
New_vaccinations numeric,
RollingPeopleVaccinated numeric
)
Insert into #PercentPopulationVaccinated
Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations, 
 SUM(CONVERT(int,vac.new_vaccinations)) OVER (Partition by dea.Location Order by 
 dea.Location, dea.Date) as RollingPeopleVaccinated
From PortfolioProject..CovidDeaths$ dea
Join PortfolioProject..CovidVaccinations$ vac
	on dea.location = vac.location
	and dea.date = vac.date
Where dea.continent is not null

Select*, (RollingPeopleVaccinated/Population)*100
From #PercentPopulationVaccinated

-- Creating view to store data for later visualizations
Create View PercentPopulationVaccinated
as
Select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations, 
 SUM(CONVERT(int,vac.new_vaccinations)) OVER (Partition by dea.Location Order by 
 dea.Location, dea.Date) as RollingPeopleVaccinated
From PortfolioProject..CovidDeaths$ dea
Join PortfolioProject..CovidVaccinations$ vac
	on dea.location = vac.location
	and dea.date = vac.date
Where dea.continent is not null


-- For Tebleau
-- Table 1
-- Global Numbers
Select  SUM(new_cases)as total_cases,SUM(cast(new_deaths as int))as total_deaths,
 SUM(cast(new_deaths as int))/SUM(new_cases)*100 as DeathPercentage
From PortfolioProject..CovidDeaths$
Where continent is not null
--Group by date
order by 1,2

--Table 2
Select location, SUM(cast(new_deaths as int)) as TotalDeathCount
From PortfolioProject..CovidDeaths$
--location like'%states%'
Where continent is null and location not in ('World', 'European Union', 'International')
Group by location
order by TotalDeathCount desc

--Table 3 
Select Location,Population, MAX(total_cases) as HighestInfectionCount, Max((total_cases/population))*100 as PercentofPopulationInected
From PortfolioProject..CovidDeaths$
-- location like'%states%'
Group by Location, population
order by PercentofPopulationInected desc

--  Table 4 
Select Location,Population,Date, MAX(total_cases) as HighestInfectionCount, Max((total_cases/population))*100 as PercentofPopulationInected
From PortfolioProject..CovidDeaths$
-- location like'%states%'
Group by Location, population, date
order by PercentofPopulationInected desc
