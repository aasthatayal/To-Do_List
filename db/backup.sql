--
-- PostgreSQL database dump
--

\restrict hvrWsWiL7g3iHQ8v5rvGNuf679cl7wRorWWxY7dvjOccuxAZT0X10g6NHA6NDXj

-- Dumped from database version 15.15
-- Dumped by pg_dump version 15.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: todo_user
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO todo_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: tasks; Type: TABLE; Schema: public; Owner: todo_user
--

CREATE TABLE public.tasks (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    due_date date,
    status character varying(50) DEFAULT 'pending'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT tasks_status_check CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'in_progress'::character varying, 'completed'::character varying])::text[])))
);


ALTER TABLE public.tasks OWNER TO todo_user;

--
-- Name: tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: todo_user
--

CREATE SEQUENCE public.tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tasks_id_seq OWNER TO todo_user;

--
-- Name: tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: todo_user
--

ALTER SEQUENCE public.tasks_id_seq OWNED BY public.tasks.id;


--
-- Name: tasks id; Type: DEFAULT; Schema: public; Owner: todo_user
--

ALTER TABLE ONLY public.tasks ALTER COLUMN id SET DEFAULT nextval('public.tasks_id_seq'::regclass);


--
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: todo_user
--

COPY public.tasks (id, title, description, due_date, status, created_at, updated_at) FROM stdin;
1	Complete FastAPI tutorial	Learn FastAPI basics and advanced features	2025-11-25	in_progress	2025-11-20 17:10:26.326116	2025-11-20 17:10:26.326116
2	Setup PostgreSQL database	Install and configure PostgreSQL for the project	2025-11-22	completed	2025-11-20 17:10:26.326116	2025-11-20 17:10:26.326116
3	Write API documentation	Document all API endpoints with examples	2025-11-28	pending	2025-11-20 17:10:26.326116	2025-11-20 17:10:26.326116
4	Design UI templates	Create responsive HTML templates for task management	2025-11-26	in_progress	2025-11-20 17:10:26.326116	2025-11-20 17:10:26.326116
5	Write unit tests	Implement comprehensive test coverage for all endpoints	2025-11-30	pending	2025-11-20 17:10:26.326116	2025-11-20 17:10:26.326116
6	Deploy to production	Setup Docker and deploy the application	2025-12-05	pending	2025-11-20 17:10:26.326116	2025-11-20 17:10:26.326116
7	Code review	Review code quality and refactor if necessary	2025-12-01	pending	2025-11-20 17:10:26.326116	2025-11-20 17:10:26.326116
8	Performance testing	Test application performance under load	2025-12-03	pending	2025-11-20 17:10:26.326116	2025-11-20 17:10:26.326116
27	Test API Task	Created via API	\N	pending	2025-11-20 17:13:23.193739	2025-11-20 17:13:23.193739
\.


--
-- Name: tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: todo_user
--

SELECT pg_catalog.setval('public.tasks_id_seq', 27, true);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: todo_user
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: idx_tasks_due_date; Type: INDEX; Schema: public; Owner: todo_user
--

CREATE INDEX idx_tasks_due_date ON public.tasks USING btree (due_date);


--
-- Name: idx_tasks_status; Type: INDEX; Schema: public; Owner: todo_user
--

CREATE INDEX idx_tasks_status ON public.tasks USING btree (status);


--
-- Name: tasks update_tasks_updated_at; Type: TRIGGER; Schema: public; Owner: todo_user
--

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON public.tasks FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- PostgreSQL database dump complete
--

\unrestrict hvrWsWiL7g3iHQ8v5rvGNuf679cl7wRorWWxY7dvjOccuxAZT0X10g6NHA6NDXj

