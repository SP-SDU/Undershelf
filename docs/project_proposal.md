# Project Proposal

## Table of Contents

1. [Background/Motivation](#backgroundmotivation)
2. [Aim](#aim)
3. [Objectives](#objectives)
4. [Solutions](#solutions)
   1. [Data Preprocessing](#data-preprocessing)
   2. [Search Module](#search-module)
   3. [Algorithmic Modules](#algorithmic-modules)
   4. [User Interface](#user-interface)
5. [Initial Requirements Analysis](#initial-requirements-analysis)
   1. [Personas](#personas)
   2. [Functional Requirements](#functional-requirements)
   3. [Non-Functional Requirements](#non-functional-requirements)
6. [Methods](#methods)
7. [Architecture](#architecture)
   1. [Component Diagram](#component-diagram)
   2. [Component Dependency Path Table](#component-dependency-path-table)
8. [Risks](#risks)
9. [Project Organization](#project-organization)
10. [Project Plan](#project-plan)
11. [Tentative Outline](#tentative-outline)

---

## Background/Motivation

In the digital age, the increasing volume of books available online has made it challenging for readers to find books that match their interests. Traditional search methods often fail to provide personalized results, leading to a frustrating user experience. Additionally, readers often struggle to discover new books that align with their preferences, as they are limited by their own knowledge or the recommendation of others.

This project addresses these challenges by developing an **Efficient Search and Recommendation System for Books**. By leveraging advanced data structures and algorithms, the system aims to provide users with fast, accurate, and personalized search results and recommendations on large datasets, ensuring scalability and performance as the number of books and users grows.

## Aim

Create an intelligent and user-friendly book search and recommendation system that helps readers discover books tailored to their interests. The platform will combine efficient search capabilities with personalized recommendations to enhance the overall reading experience and support seamless exploration of new titles.

## Objectives

1. **Fast and Smart Search**

   * Use a Binary Search Tree (BST) for quick lookups.
   * Provide autocomplete suggestions.
   * Support searches by title, author, and genre.

2. **Efficient Sorting**

   * Implement Merge Sort, Quick Sort, or Heap Sort to organize books by ratings, reviews, and publication year.
   * Ensure sorting scales to large datasets.

3. **Graph‑Based Recommendations**

   * Model books as nodes and edges for co‑purchases, genre similarity, and author collaborations.
   * Use BFS or Dijkstra’s Algorithm to traverse and suggest related titles.

4. **Heap‑Based Ranking**

   * Maintain a Min‑Heap/Max‑Heap for Top‑K popular or highest‑rated books.
   * Enable O(log n) retrieval of top items.

5. **Scalability & Performance**

   * Optimize for large datasets, keeping search response under 2 s.
   * Write modular, maintainable code.

## Solutions

### Data Preprocessing

* Transform the Amazon Book Dataset into structured format.
* Handle missing values, standardize date formats, and normalize text.

### Search Module

* Multilayer queries over titles, descriptions, authors, etc.
* Features: autocomplete, dynamic filtering, and smart suggestions.

### Algorithmic Modules

* Hybrid strategies: graph‑based recommendations, similarity measures, popularity ranking, etc.

### User Interface

* Dashboard for search results and recommendations.
* Context menus and filters to navigate algorithm outputs.
* Emphasis on accessibility and usability.

## Initial Requirements Analysis

### Personas

| Role             | Responsible For                                    | Needs                                          | Goals                                      | Challenges                                                 |
| ---------------- | -------------------------------------------------- | ---------------------------------------------- | ------------------------------------------ | ---------------------------------------------------------- |
| Reader/User      | Discover and explore books                         | Simple interface, relevant results             | Find and save interesting books            | Irrelevant results, poor recommendations, slow performance |
| Security Officer | Protect user data and system                       | Secure storage, unauthorized access prevention | Maintain data privacy and system integrity | Breaches, vulnerabilities, unauthorized data access        |
| Developer        | Design, implement, test, maintain                  | Clear requirements, robust architecture        | Build efficient, maintainable system       | Understanding complexity, debugging, performance tuning    |
| Admin            | Manage book data, system configuration, monitoring | CRUD tools, dashboards                         | Ensure system health and data accuracy     | Downtime, data integrity, scaling challenges               |

### Functional Requirements

| ID | User Story                                                                                   | MoSCoW      |
| -- | -------------------------------------------------------------------------------------------- | ----------- |
| F1 | As a Reader, I want to search by title, author, genre so I can find books that interest me.  | Must Have   |
| F2 | As a Reader, I want autocomplete suggestions as I type my query to speed up searches.        | Must Have   |
| F3 | As a Reader, I want recommendations based on history and preferences to discover new titles. | Must Have   |
| F4 | As a Reader, I want to see top-rated books to widen my horizons.                             | Should Have |
| F5 | As an Admin, I want to import/manage book data for up-to-date content.                       | Must Have   |
| F6 | As an Admin, I want an admin panel to view system statistics.                                | Should Have |

### Non-Functional Requirements

| ID  | Requirement                                                       | MoSCoW      |
| --- | ----------------------------------------------------------------- | ----------- |
| NF1 | Search results respond in ≤ 2 s for a smooth experience.          | Must Have   |
| NF2 | System scales with large datasets for growth.                     | Must Have   |
| NF3 | Code is modular and documented for maintainability.               | Must Have   |
| NF4 | Interface is easy to use for low friction.                        | Should Have |
| NF5 | Ensure data security to protect user information from bad actors. | Should Have |

## Methods

* **Agile (Scrum)**

  * Two-week sprints, weekly scrum meetings.
  * Test-Driven Development (TDD).
* **Tools**: Communication via Discord/E‑mail; GitHub Projects; Git & GitHub Desktop; VS Code.
* **Tech Stack**: Python; Flask (optional); MongoDB; NetworkX for graph algorithms.

## Architecture

### Component Diagram

![Diagram of a Book Search System showing interconnected modules for User Interface, Search, Recommendation, Ranking, and Sorting, supported by a Database, Algorithm Libraries, and a Data Preprocessing unit, with data flow arrows illustrating query processing, book retrieval, and ranking logic.](data:image/avif;base64,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)

### Component Dependency Path Table

| Component             | Direct Dependencies                  | Dependency Depth |
| --------------------- | ------------------------------------ | ---------------- |
| User Interface        | Search, Recommendation, Ranking      | 1                |
| Search Module         | Data Preprocessing, BST/Autocomplete | 1                |
| Sorting Module        | Search Module                        | 1                |
| Recommendation Module | Graph Traversal Library              | 1                |
| Ranking Module        | Heap Library                         | 1                |
| Data Preprocessing    | Datasets                             | 0                |
| Database              | —                                    | 0                |

## Risks

| Risk                              | Severity | Mitigation                                        |
| --------------------------------- | -------- | ------------------------------------------------- |
| Complexity of component design    | High     | Regular TDD and integration testing               |
| Expensive algorithms              | High     | Start with simpler algorithms, test incrementally |
| Performance bottlenecks           | Medium   | Indexing, caching, and algorithmic optimizations  |
| Inexperience with Python AI stack | Medium   | Training sessions and pair programming            |
| Scheduling inaccuracies           | Medium   | Break tasks into one‑day subtasks                 |
| Large dataset handling            | Medium   | Develop on small subsets, optimize loading        |
| Scope creep                       | Low      | Strict MVP definition and feature prioritization  |
| Team collaboration challenges     | Low      | Weekly sync meetings and clear role assignments   |

## Project Organization

* **Product Owner**: Manages backlog and defines product vision.
* **Scrum Master**: Removes blockers, facilitates weekly scrums.
* **Quality Assurance (QA)**: Ensures TDD compliance and test coverage.
* **Developers**: Implement features and maintain code.
* **Admin**: Manages data imports and system monitoring.

## Project Plan

**Sprints (2‑week cycles):**

1. Setup & Design
2. Search Module Implementation
3. Sorting & Recommendation Module
4. Ranking & Recommendation Refinement
5. User Interface Development
6. Finalization & Documentation

## Tentative Outline

1. Introduction: Overview and scope.
2. Background & Motivation: Relevance and stakeholders.
3. Problem Statement & Objectives: Challenges and remedies.
4. System Architecture & Design: Frontend, backend, database.
5. Project Management & Methods: Tools and methodologies.
6. Risk Analysis: Risks and mitigations.
7. Testing & Validation: Strategies for security and reliability.
8. Results & Discussion: Outcomes analysis.
9. Conclusion
10. References
11. Appendices
