/*
 * Embabel Multi-Tool Agent (Java) — Compare with module01_raw/1.5_tools_multi
 * =============================================================================
 *
 * WHAT THIS SHOWS (capabilities unique to Embabel):
 *   1. Goal-directed agents  — declare WHAT the agent should achieve, not HOW
 *   2. @Action annotations   — Spring-managed tool functions with conditions
 *   3. Automatic planning    — Embabel picks the action sequence to reach a goal
 *   4. Spring DI integration — tools are injectable beans, not loose functions
 *   5. Condition guards      — actions fire only when domain state matches
 *
 * WHY THIS MATTERS vs Python approaches:
 *   • Raw Python (module01): manually route tool calls in if/elif chains
 *   • LangChain (module03): agent loop with tool list, still imperative
 *   • DSPy: optimizes prompts, but you still code the pipeline
 *   • Embabel: you declare a GOAL + annotated actions, the framework plans
 *
 * SCENARIO: Same multi-tool weather+pincode agent as module01_raw/1.5_tools_multi,
 *           but expressed as goal-directed actions with condition guards.
 *
 * PREREQUISITES:
 *   - JDK 21+
 *   - Maven or Gradle
 *   - Add to pom.xml:
 *       <dependency>
 *           <groupId>com.embabel</groupId>
 *           <artifactId>embabel-agent-api</artifactId>
 *           <version>0.5.0</version>
 *       </dependency>
 *   - An Ollama-compatible endpoint (Embabel supports OpenAI-compatible APIs)
 *
 * RUN:
 *   mvn spring-boot:run
 *   (or run from your IDE as a Spring Boot application)
 *
 * NOTE: This is a Java/Spring file — it cannot run in the Python environment.
 *       It is included as a reference sample so students can compare the
 *       architectural approach side-by-side with the Python modules.
 */

package com.example.agenticai.embabel;

import com.embabel.agent.api.annotation.Action;
import com.embabel.agent.api.annotation.Agent;
import com.embabel.agent.api.annotation.Goal;
import com.embabel.agent.api.common.OperationContext;
import com.embabel.agent.api.AgentPlatform;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ApplicationContext;
import org.springframework.stereotype.Component;

// ---------------------------------------------------------------------------
// 1. Domain object — typed state (compare: raw Python uses plain dicts)
// ---------------------------------------------------------------------------

class CityQuery {
    private final String city;
    private String weather;
    private String pincode;
    private String summary;

    public CityQuery(String city) {
        this.city = city;
    }

    // Private constructor for internal copy
    private CityQuery(String city, String weather, String pincode, String summary) {
        this.city = city;
        this.weather = weather;
        this.pincode = pincode;
        this.summary = summary;
    }

    public String getCity()    { return city; }
    public String getWeather() { return weather; }
    public String getPincode() { return pincode; }
    public String getSummary() { return summary; }

    /** Immutable-style copy with updated weather. */
    public CityQuery withWeather(String weather) {
        return new CityQuery(this.city, weather, this.pincode, this.summary);
    }

    /** Immutable-style copy with updated pincode. */
    public CityQuery withPincode(String pincode) {
        return new CityQuery(this.city, this.weather, pincode, this.summary);
    }

    /** Immutable-style copy with updated summary. */
    public CityQuery withSummary(String summary) {
        return new CityQuery(this.city, this.weather, this.pincode, summary);
    }
}

// ---------------------------------------------------------------------------
// 2. Tool functions as Spring beans (compare: module01 loose functions)
// ---------------------------------------------------------------------------

@Component
class WeatherService {
    public String lookup(String city) {
        return city + ": +12°C, partly cloudy";
    }
}

@Component
class PincodeService {
    public String lookup(String city) {
        return city + ": 123456";
    }
}

// ---------------------------------------------------------------------------
// 3. Embabel Agent — goal-directed with @Action annotations
//
//    KEY DIFFERENCE: In module01_raw/1.5_tools_multi the developer writes
//    the routing logic (if function_name == "get_weather" ...).
//    Here, the framework inspects the domain state and picks which actions
//    to run to reach the declared @Goal.
// ---------------------------------------------------------------------------

@Agent(description = "Multi-tool city information agent")
class CityInfoAgent {

    private final WeatherService weatherService;
    private final PincodeService pincodeService;

    // Constructor injection — standard Spring DI
    public CityInfoAgent(WeatherService weatherService, PincodeService pincodeService) {
        this.weatherService = weatherService;
        this.pincodeService = pincodeService;
    }

    // Action: fires when weather is NOT yet resolved
    @Action(description = "Fetch weather for the city")
    public CityQuery fetchWeather(CityQuery query, OperationContext ctx) {
        if (query.getWeather() != null) return query;          // guard: already done
        String result = weatherService.lookup(query.getCity());
        System.out.println("  [Action] fetchWeather(" + query.getCity() + ") → " + result);
        return query.withWeather(result);
    }

    // Action: fires when pincode is NOT yet resolved
    @Action(description = "Fetch pincode for the city")
    public CityQuery fetchPincode(CityQuery query, OperationContext ctx) {
        if (query.getPincode() != null) return query;          // guard: already done
        String result = pincodeService.lookup(query.getCity());
        System.out.println("  [Action] fetchPincode(" + query.getCity() + ") → " + result);
        return query.withPincode(result);
    }

    // Action: fires when both weather AND pincode are present, uses LLM
    @Action(description = "Summarize city info using LLM")
    public CityQuery summarize(CityQuery query, OperationContext ctx) {
        if (query.getWeather() == null || query.getPincode() == null) return query;
        if (query.getSummary() != null) return query;

        String prompt = String.format(
            "Summarize the following city information in one sentence:%n" +
            "City: %s%nWeather: %s%nPincode: %s",
            query.getCity(), query.getWeather(), query.getPincode()
        );

        String llmAnswer = ctx.getLlm().generate(prompt);
        System.out.println("  [Action] summarize → " + llmAnswer);
        return query.withSummary(llmAnswer);
    }

    // Goal: the agent is done when summary is populated
    @Goal(description = "Produce a complete city info summary")
    public boolean isComplete(CityQuery query) {
        return query.getSummary() != null;
    }
}

// ---------------------------------------------------------------------------
// 4. Spring Boot entry point
// ---------------------------------------------------------------------------

@SpringBootApplication
public class EmbabelDemoApplication {

    public static void main(String[] args) {
        ApplicationContext ctx = SpringApplication.run(EmbabelDemoApplication.class, args);
        CityInfoAgent agent = ctx.getBean(CityInfoAgent.class);
        AgentPlatform platform = ctx.getBean(AgentPlatform.class);

        System.out.println("=== Embabel Multi-Tool Agent (compare with module01_raw/1.5_tools_multi) ===\n");

        CityQuery query = new CityQuery("Bogotá");
        System.out.println("Query: Tell me about " + query.getCity() + "\n");

        // The platform plans and executes actions automatically to reach the goal
        CityQuery result = (CityQuery) platform.runAgent(agent, query);

        System.out.println("\nFinal summary: " + result.getSummary());
        System.out.println();
        System.out.println("KEY TAKEAWAY: Embabel replaces imperative tool-routing with");
        System.out.println("goal-directed actions.  You declare actions + a goal condition;");
        System.out.println("the framework plans the execution order automatically.");
        System.out.println("Spring DI means tools are testable, injectable beans.");
    }
}

/*
 * COMPARISON TABLE (for student reference):
 *
 * ┌─────────────────┬────────────────────────────────────────────────────────┐
 * │ Aspect          │ Raw Python          LangChain       DSPy      Embabel │
 * ├─────────────────┼────────────────────────────────────────────────────────┤
 * │ Tool routing    │ Manual if/elif      Agent loop      Module    @Action │
 * │ Prompt mgmt     │ Hand-written        Templates       Optimized Auto    │
 * │ State tracking  │ Dicts               Memory obj      Trace     Domain  │
 * │ Planning        │ None                ReAct/Plan      Chain     Goal    │
 * │ DI / Testing    │ None                Partial         None      Spring  │
 * │ Language        │ Python              Python          Python    Java    │
 * └─────────────────┴────────────────────────────────────────────────────────┘
 */
