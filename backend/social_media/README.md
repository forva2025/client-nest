# Facebook Integration API Endpoints

This document lists the backend API endpoints available for Facebook Page management and analytics.

## Endpoints

- **GET /api/facebook/posts/**
  - List all Facebook posts for the page.

- **GET /api/facebook/posts/<post_id>/**
  - Get details for a specific Facebook post.

- **POST /api/facebook/posts/**
  - Create a new post on the Facebook page.

- **GET /api/facebook/posts/<post_id>/comments/**
  - Get all comments for a specific post.

- **GET /api/facebook/posts/<post_id>/reactions/**
  - Get reaction counts for a specific post.

- **GET /api/facebook/posts/<post_id>/insights/**
  - Get analytics (impressions, engagement, etc.) for a specific post.

---

**Note:**
- These endpoints are to be consumed by the frontend for Facebook Page management and analytics.
- Do not include sensitive information (like access tokens) in frontend code or documentation. 