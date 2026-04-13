/*
 * Embabel Multi-Tool Agent — Compare with module01_raw/1.5_tools_multi
 * =====================================================================
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
 * NOTE: This is a Kotlin/Spring file — it cannot run in the Python environment.
 *       It is included as a reference sample so students can compare the
 *       architectural approach side-by-side with the Python modules.
 */

package com.example.agenticai.embabel

import com.embabel.agent.api.annotation.Action
import com.embabel.agent.api.annotation.Agent
import com.embabel.agent.api.annotation.Goal
import com.embabel.agent.api.common.OperationContext
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.stereotype.Component

// ---------------------------------------------------------------------------
// 1. Domain objects — typed state (compare: raw Python uses plain dicts)
// ---------------------------------------------------------------------------

data class CityQuery(
    val city: String,
    val weather: String? = null,
    val pincode: String? = null,
    val summary: String? = null,
)

// ---------------------------------------------------------------------------
// 2. Tool functions as Spring beans (compare: module01 loose functions)
// ---------------------------------------------------------------------------

@Component
class WeatherService {
    fun lookup(city: String): String = "$city: +12°C, partly cloudy"
}

@Component
class PincodeService {
    fun lookup(city: String): String = "$city: 123456"
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
class CityInfoAgent(
    private val weatherService: WeatherService,
    private val pincodeService: PincodeService,
) {

    // Action: fires when weather is NOT yet resolved
    @Action(description = "Fetch weather for the city")
    fun fetchWeather(query: CityQuery, ctx: OperationContext): CityQuery {
        if (query.weather != null) return query            // guard: already done
        val result = weatherService.lookup(query.city)
        println("  [Action] fetchWeather(${query.city}) → $result")
        return query.copy(weather = result)
    }

    // Action: fires when pincode is NOT yet resolved
    @Action(description = "Fetch pincode for the city")
    fun fetchPincode(query: CityQuery, ctx: OperationContext): CityQuery {
        if (query.pincode != null) return query             // guard: already done
        val result = pincodeService.lookup(query.city)
        println("  [Action] fetchPincode(${query.city}) → $result")
        return query.copy(pincode = result)
    }

    // Action: fires when both weather AND pincode are present, uses LLM
    @Action(description = "Summarize city info using LLM")
    fun summarize(query: CityQuery, ctx: OperationContext): CityQuery {
        if (query.weather == null || query.pincode == null) return query
        if (query.summary != null) return query

        val prompt = """
            |Summarize the following city information in one sentence:
            |City: ${query.city}
            |Weather: ${query.weather}
            |Pincode: ${query.pincode}
        """.trimMargin()

        val llmAnswer = ctx.llm.generate(prompt)
        println("  [Action] summarize → $llmAnswer")
        return query.copy(summary = llmAnswer)
    }

    // Goal: the agent is done when summary is populated
    @Goal(description = "Produce a complete city info summary")
    fun isComplete(query: CityQuery): Boolean =
        query.summary != null
}

// ---------------------------------------------------------------------------
// 4. Spring Boot entry point
// ---------------------------------------------------------------------------

@SpringBootApplication
class EmbabelDemoApplication

fun main(args: Array<String>) {
    val ctx = runApplication<EmbabelDemoApplication>(*args)
    val agent = ctx.getBean(CityInfoAgent::class.java)
    val platform = ctx.getBean(com.embabel.agent.api.AgentPlatform::class.java)

    println("=== Embabel Multi-Tool Agent (compare with module01_raw/1.5_tools_multi) ===\n")

    val query = CityQuery(city = "Bogotá")
    println("Query: Tell me about ${query.city}\n")

    // The platform plans and executes actions automatically to reach the goal
    val result = platform.runAgent(agent, query)

    println("\nFinal summary: ${result.summary}")
    println()
    println("KEY TAKEAWAY: Embabel replaces imperative tool-routing with")
    println("goal-directed actions.  You declare actions + a goal condition;")
    println("the framework plans the execution order automatically.")
    println("Spring DI means tools are testable, injectable beans.")
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
 * │ Language        │ Python              Python          Python    Kotlin  │
 * └─────────────────┴────────────────────────────────────────────────────────┘
 */
