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

![Diagram of a Book Search System showing interconnected modules for User Interface, Search, Recommendation, Ranking, and Sorting, supported by a Database, Algorithm Libraries, and a Data Preprocessing unit, with data flow arrows illustrating query processing, book retrieval, and ranking logic.](data:image/webp;base64,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)

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
