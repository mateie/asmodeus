from ddgs import DDGS # pyright: ignore[reportUnknownVariableType]

class Web:
    def __init__(self):
        self.tools = {f.__name__: f for f in (self.search_web,)}
    
    def search_web(self, query: str) -> str:
        """Search the web for current information, news, or facts you don't know.

        Args:
            query: A short search query, like 'rtx 5070 price' or 'weather in Arcata'.
        """
        try:
            results = DDGS().text(query, max_results=5)
            if not results:
                return "No results found."
            
            return "\n\n".join(
                f"{r['title']}\n{r['href']}\n{r['body'][:300]}" for r in results
            )
        except Exception as e:
            return f"Error: {e}"